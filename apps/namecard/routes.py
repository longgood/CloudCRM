# -*- encoding: utf-8 -*-

import os
import json
import uuid
import datetime
import logging

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from apps.namecard import blueprint
from apps.namecard.models import BusinessCard, OutboundDraft
from apps import db

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload a business card image, run OCR and LLM extraction."""
    if request.method == 'GET':
        return render_template('namecard/upload.html', segment='namecard_upload')

    # Handle POST - file upload
    if 'file' not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for('namecard_blueprint.upload'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected.", "error")
        return redirect(url_for('namecard_blueprint.upload'))

    if not allowed_file(file.filename):
        flash("Invalid file type. Please upload an image (png, jpg, jpeg, gif).", "error")
        return redirect(url_for('namecard_blueprint.upload'))

    try:
        # Save file
        upload_dir = current_app.config.get('UPLOAD_FOLDER_NAMECARD', 'data/namecard')
        user_dir = os.path.join(upload_dir, str(current_user.uid))
        os.makedirs(user_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(user_dir, unique_name)
        file.save(file_path)

        # Create DB record
        card = BusinessCard(
            user_id=current_user.uid,
            image_path=file_path,
            original_filename=filename,
            status='uploaded'
        )
        db.session.add(card)
        db.session.commit()

        # Run OCR
        ocr_text = ''
        try:
            from apps.namecard.services.ocr import get_ocr_engine
            engine = get_ocr_engine(
                'tesseract',
                tesseract_cmd=current_app.config.get('TESSERACT_CMD', 'tesseract')
            )
            ocr_text = engine.extract_text(file_path)
            card.ocr_text = ocr_text
            card.status = 'ocr_done'
            db.session.commit()
        except Exception as e:
            logger.error(f"OCR failed for card {card.id}: {e}")
            card.ocr_text = f"OCR Error: {str(e)}"
            card.status = 'ocr_error'
            db.session.commit()

        # Run LLM extraction
        extracted = {}
        api_key = current_app.config.get('OPENAI_API_KEY', '')
        if ocr_text and api_key:
            try:
                from apps.namecard.services.llm import extract_card_info
                extracted = extract_card_info(ocr_text, api_key)
                card.extracted_json = json.dumps(extracted, ensure_ascii=False)
                card.status = 'extracted'
                db.session.commit()
            except Exception as e:
                logger.error(f"LLM extraction failed for card {card.id}: {e}")
                card.status = 'extract_error'
                db.session.commit()
        elif not api_key:
            logger.warning("OPENAI_API_KEY not configured, skipping LLM extraction")

        return render_template('namecard/upload.html',
                               segment='namecard_upload',
                               card=card,
                               ocr_text=ocr_text,
                               extracted=extracted)

    except Exception as e:
        logger.error(f"Upload error: {e}")
        flash(f"Upload failed: {str(e)}", "error")
        return redirect(url_for('namecard_blueprint.upload'))


@blueprint.route('/extract', methods=['POST'])
@login_required
def extract():
    """Re-run LLM extraction with edited OCR text."""
    card_id = request.form.get('card_id', type=int)
    ocr_text = request.form.get('ocr_text', '')

    card = BusinessCard.query.filter_by(id=card_id, user_id=current_user.uid).first()
    if not card:
        flash("Card not found.", "error")
        return redirect(url_for('namecard_blueprint.upload'))

    card.ocr_text = ocr_text
    db.session.commit()

    api_key = current_app.config.get('OPENAI_API_KEY', '')
    if not api_key:
        flash("OpenAI API key not configured.", "error")
        return redirect(url_for('namecard_blueprint.card_detail', card_id=card.id))

    try:
        from apps.namecard.services.llm import extract_card_info
        extracted = extract_card_info(ocr_text, api_key)
        card.extracted_json = json.dumps(extracted, ensure_ascii=False)
        card.status = 'extracted'
        db.session.commit()
    except Exception as e:
        logger.error(f"Re-extraction failed for card {card.id}: {e}")
        flash(f"Extraction failed: {str(e)}", "error")
        extracted = {}

    return render_template('namecard/upload.html',
                           segment='namecard_upload',
                           card=card,
                           ocr_text=ocr_text,
                           extracted=extracted)


@blueprint.route('/draft', methods=['POST'])
@login_required
def draft():
    """Generate email draft from extracted card info + user prompt."""
    card_id = request.form.get('card_id', type=int)
    user_prompt = request.form.get('user_prompt', '')

    # Allow user to edit extracted fields
    extracted = {
        'name': request.form.get('name', ''),
        'title': request.form.get('title', ''),
        'company': request.form.get('company', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'address': request.form.get('address', ''),
        'website': request.form.get('website', ''),
        'notes': request.form.get('notes', ''),
    }

    card = BusinessCard.query.filter_by(id=card_id, user_id=current_user.uid).first()
    if not card:
        flash("Card not found.", "error")
        return redirect(url_for('namecard_blueprint.cards'))

    # Update extracted JSON with edited fields
    card.extracted_json = json.dumps(extracted, ensure_ascii=False)
    db.session.commit()

    to_email = extracted.get('email', '')
    if not to_email:
        flash("No email found on the business card. Please enter the recipient's email.", "error")
        return render_template('namecard/upload.html',
                               segment='namecard_upload',
                               card=card,
                               ocr_text=card.ocr_text or '',
                               extracted=extracted)

    api_key = current_app.config.get('OPENAI_API_KEY', '')
    company_template = current_app.config.get('COMPANY_INTRO_TEMPLATE', '')

    subject = ''
    body = ''
    if api_key:
        try:
            from apps.namecard.services.llm import generate_draft
            result = generate_draft(extracted, user_prompt, company_template, api_key)
            subject = result.get('subject', '')
            body = result.get('body', '')
        except Exception as e:
            logger.error(f"Draft generation failed: {e}")
            flash(f"Draft generation failed: {str(e)}", "error")
    else:
        flash("OpenAI API key not configured. Please write the email manually.", "error")

    return render_template('namecard/draft_compose.html',
                           segment='namecard_draft',
                           card=card,
                           extracted=extracted,
                           to_email=to_email,
                           subject=subject,
                           body=body,
                           user_prompt=user_prompt)


@blueprint.route('/send', methods=['POST'])
@login_required
def send():
    """Send the draft email via Gmail API."""
    from apps.gmail.models import GmailAccount
    from apps.gmail.services.oauth import build_gmail_service
    from apps.namecard.services.gmail_send import create_message, send_message

    card_id = request.form.get('card_id', type=int)
    to_email = request.form.get('to_email', '')
    subject = request.form.get('subject', '')
    body = request.form.get('body', '')
    user_prompt = request.form.get('user_prompt', '')

    if not to_email:
        flash("Recipient email is required.", "error")
        return redirect(url_for('namecard_blueprint.cards'))

    card = BusinessCard.query.filter_by(id=card_id, user_id=current_user.uid).first()
    if not card:
        flash("Card not found.", "error")
        return redirect(url_for('namecard_blueprint.cards'))

    # Check Gmail connection
    gmail_account = GmailAccount.query.filter_by(user_id=current_user.uid).first()
    if not gmail_account:
        flash("Please connect your Gmail account first.", "error")
        return redirect(url_for('gmail_blueprint.connect'))

    try:
        service = build_gmail_service(gmail_account)
        message = create_message(
            sender=gmail_account.google_email,
            to=to_email,
            subject=subject,
            body_text=body
        )
        result = send_message(service, message)

        # Create outbound draft record
        draft_record = OutboundDraft(
            user_id=current_user.uid,
            business_card_id=card.id,
            to_email=to_email,
            subject=subject,
            body=body,
            user_prompt=user_prompt,
            status='sent',
            gmail_message_id=result.get('id', ''),
            sent_at=datetime.datetime.utcnow()
        )
        db.session.add(draft_record)
        db.session.commit()

        logger.info(f"Email sent to {to_email} for card {card.id}, gmail_msg_id={result.get('id')}")
        flash(f"Email sent to {to_email}!", "success")

    except Exception as e:
        logger.error(f"Send failed: {e}")
        flash(f"Send failed: {str(e)}", "error")

        # Save as draft
        draft_record = OutboundDraft(
            user_id=current_user.uid,
            business_card_id=card.id,
            to_email=to_email,
            subject=subject,
            body=body,
            user_prompt=user_prompt,
            status='draft'
        )
        db.session.add(draft_record)
        db.session.commit()

    return redirect(url_for('namecard_blueprint.cards'))


@blueprint.route('/cards')
@login_required
def cards():
    """List all uploaded business cards for the current user."""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = (BusinessCard.query
                  .filter_by(user_id=current_user.uid)
                  .order_by(BusinessCard.created_at.desc())
                  .paginate(page=page, per_page=per_page, error_out=False))

    return render_template('namecard/card_list.html',
                           segment='namecard_cards',
                           cards=pagination.items,
                           pagination=pagination)


@blueprint.route('/card/<int:card_id>')
@login_required
def card_detail(card_id):
    """Show card detail with extracted data and drafts."""
    card = BusinessCard.query.filter_by(id=card_id, user_id=current_user.uid).first()
    if not card:
        flash("Card not found.", "error")
        return redirect(url_for('namecard_blueprint.cards'))

    extracted = {}
    if card.extracted_json:
        try:
            extracted = json.loads(card.extracted_json)
        except (json.JSONDecodeError, TypeError):
            pass

    drafts = OutboundDraft.query.filter_by(business_card_id=card.id).order_by(OutboundDraft.created_at.desc()).all()

    return render_template('namecard/upload.html',
                           segment='namecard_upload',
                           card=card,
                           ocr_text=card.ocr_text or '',
                           extracted=extracted,
                           drafts=drafts)


@blueprint.route('/image/<int:card_id>')
@login_required
def serve_image(card_id):
    """Serve the business card image (only to the owner)."""
    card = BusinessCard.query.filter_by(id=card_id, user_id=current_user.uid).first()
    if not card or not os.path.exists(card.image_path):
        return "Not found", 404
    return send_file(card.image_path)
