# -*- encoding: utf-8 -*-

import datetime
from apps import db


class BusinessCard(db.Model):
    """An uploaded business card image and its OCR/LLM extraction."""
    __tablename__ = 'business_cards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('TManager.uid'), nullable=False, index=True)
    image_path = db.Column(db.String(512), nullable=False)
    original_filename = db.Column(db.String(256), nullable=True)
    ocr_text = db.Column(db.Text, nullable=True)
    extracted_json = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default='uploaded')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    drafts = db.relationship('OutboundDraft', backref='business_card', lazy='dynamic')


class OutboundDraft(db.Model):
    """A draft email generated from a business card."""
    __tablename__ = 'outbound_drafts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('TManager.uid'), nullable=False, index=True)
    business_card_id = db.Column(db.Integer, db.ForeignKey('business_cards.id'), nullable=False)
    to_email = db.Column(db.String(256), nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_prompt = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(16), default='draft')
    gmail_message_id = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
