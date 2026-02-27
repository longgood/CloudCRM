# -*- encoding: utf-8 -*-

import logging
from flask import render_template, redirect, url_for, request, session, flash, jsonify
from flask_login import login_required, current_user

from apps.gmail import blueprint
from apps.gmail.models import GmailAccount, EmailMessage, EmailContact
from apps.gmail.services.oauth import get_authorization_url, exchange_code, build_gmail_service
from apps.gmail.services.crypto import encrypt_token
from apps import db

logger = logging.getLogger(__name__)


@blueprint.route('/connect')
@login_required
def connect():
    """Show Gmail connection status or redirect to OAuth."""
    gmail_account = GmailAccount.query.filter_by(user_id=current_user.uid).first()
    return render_template('gmail/oauth_connect.html',
                           segment='gmail_connect',
                           gmail_account=gmail_account)


@blueprint.route('/authorize')
@login_required
def authorize():
    """Start Google OAuth flow - redirect to Google consent screen."""
    try:
        auth_url, state = get_authorization_url()
        session['oauth_state'] = state
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"OAuth authorization error: {e}")
        flash(f"Failed to start OAuth: {str(e)}", "error")
        return redirect(url_for('gmail_blueprint.connect'))


@blueprint.route('/callback')
@login_required
def callback():
    """Handle Google OAuth callback."""
    try:
        state = session.pop('oauth_state', None)
        if not state:
            flash("Invalid OAuth state. Please try again.", "error")
            return redirect(url_for('gmail_blueprint.connect'))

        code = request.args.get('code')
        if not code:
            flash("No authorization code received.", "error")
            return redirect(url_for('gmail_blueprint.connect'))

        credentials = exchange_code(code, state)

        if not credentials.refresh_token:
            flash("No refresh token received. Please try again.", "error")
            return redirect(url_for('gmail_blueprint.connect'))

        # Get user's Gmail address
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        google_email = profile['emailAddress']

        # Encrypt and store tokens
        encrypted_refresh = encrypt_token(credentials.refresh_token)

        gmail_account = GmailAccount.query.filter_by(user_id=current_user.uid).first()
        if gmail_account:
            gmail_account.google_email = google_email
            gmail_account.encrypted_refresh_token = encrypted_refresh
            gmail_account.scopes = ','.join(credentials.scopes) if credentials.scopes else ''
        else:
            gmail_account = GmailAccount(
                user_id=current_user.uid,
                google_email=google_email,
                encrypted_refresh_token=encrypted_refresh,
                scopes=','.join(credentials.scopes) if credentials.scopes else ''
            )
            db.session.add(gmail_account)

        db.session.commit()
        logger.info(f"Gmail account connected for user {current_user.uid}: {google_email}")
        flash(f"Gmail connected: {google_email}", "success")

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        flash(f"OAuth error: {str(e)}", "error")

    return redirect(url_for('gmail_blueprint.connect'))


@blueprint.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Gmail account."""
    gmail_account = GmailAccount.query.filter_by(user_id=current_user.uid).first()
    if gmail_account:
        # Delete associated messages and contacts
        EmailMessage.query.filter_by(user_id=current_user.uid).delete()
        EmailContact.query.filter_by(user_id=current_user.uid).delete()
        db.session.delete(gmail_account)
        db.session.commit()
        logger.info(f"Gmail account disconnected for user {current_user.uid}")
        flash("Gmail account disconnected.", "success")
    return redirect(url_for('gmail_blueprint.connect'))


@blueprint.route('/sync', methods=['POST'])
@login_required
def sync():
    """Trigger Gmail sync manually."""
    from apps.gmail.services.sync import sync_gmail

    gmail_account = GmailAccount.query.filter_by(user_id=current_user.uid).first()
    if not gmail_account:
        flash("Please connect your Gmail account first.", "error")
        return redirect(url_for('gmail_blueprint.connect'))

    days = request.form.get('days', 365, type=int)
    try:
        count = sync_gmail(current_user.uid, days=days)
        flash(f"Sync complete. Processed {count} messages.", "success")
    except Exception as e:
        logger.error(f"Gmail sync error for user {current_user.uid}: {e}")
        flash(f"Sync failed: {str(e)}", "error")

    return redirect(url_for('gmail_blueprint.contacts'))


@blueprint.route('/contacts')
@login_required
def contacts():
    """Email Contacts page with level filter and search."""
    gmail_account = GmailAccount.query.filter_by(user_id=current_user.uid).first()
    if not gmail_account:
        flash("Please connect your Gmail account first.", "error")
        return redirect(url_for('gmail_blueprint.connect'))

    level_filter = request.args.get('level', '', type=str)
    search_query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 50

    query = EmailContact.query.filter_by(user_id=current_user.uid)

    if level_filter != '':
        query = query.filter(EmailContact.level == int(level_filter))

    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            db.or_(
                EmailContact.contact_email.ilike(search_like),
                EmailContact.contact_name.ilike(search_like)
            )
        )

    query = query.order_by(EmailContact.last_interaction_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('gmail/email_contacts.html',
                           segment='gmail_contacts',
                           gmail_account=gmail_account,
                           contacts=pagination.items,
                           pagination=pagination,
                           level_filter=level_filter,
                           search_query=search_query)


@blueprint.route('/api/contacts')
@login_required
def api_contacts():
    """JSON API for contacts (AJAX)."""
    level_filter = request.args.get('level', '', type=str)
    search_query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 50

    query = EmailContact.query.filter_by(user_id=current_user.uid)

    if level_filter != '':
        query = query.filter(EmailContact.level == int(level_filter))

    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            db.or_(
                EmailContact.contact_email.ilike(search_like),
                EmailContact.contact_name.ilike(search_like)
            )
        )

    query = query.order_by(EmailContact.last_interaction_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    contacts_data = []
    for c in pagination.items:
        contacts_data.append({
            'id': c.id,
            'email': c.contact_email,
            'name': c.contact_name or '',
            'level': c.level,
            'inbound_count': c.inbound_count,
            'outbound_count': c.outbound_count,
            'last_interaction': c.last_interaction_at.strftime('%Y-%m-%d') if c.last_interaction_at else '',
            'last_subject': c.last_subject or ''
        })

    return jsonify({
        'contacts': contacts_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })


# Import build here to avoid circular imports
from googleapiclient.discovery import build
