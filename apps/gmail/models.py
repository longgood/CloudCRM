# -*- encoding: utf-8 -*-

import datetime
from apps import db


class GmailAccount(db.Model):
    """Stores Google OAuth credentials per CRM user."""
    __tablename__ = 'gmail_accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('TManager.uid'), nullable=False, index=True)
    google_email = db.Column(db.String(256), nullable=False)
    encrypted_refresh_token = db.Column(db.Text, nullable=False)
    encrypted_access_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    scopes = db.Column(db.String(512), nullable=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'google_email', name='uq_user_gmail'),
    )


class EmailMessage(db.Model):
    """Cached Gmail messages (metadata only)."""
    __tablename__ = 'email_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('TManager.uid'), nullable=False)
    message_id = db.Column(db.String(64), nullable=False)
    thread_id = db.Column(db.String(64), nullable=False)
    from_email = db.Column(db.String(256), nullable=False)
    to_emails = db.Column(db.Text, nullable=True)
    cc_emails = db.Column(db.Text, nullable=True)
    subject = db.Column(db.Text, nullable=True)
    snippet = db.Column(db.Text, nullable=True)
    internal_date = db.Column(db.DateTime, nullable=False)
    labels = db.Column(db.Text, nullable=True)
    direction = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'message_id', name='uq_user_message'),
        db.Index('ix_user_internal_date', 'user_id', 'internal_date'),
    )


class EmailContact(db.Model):
    """Aggregated contact interaction data."""
    __tablename__ = 'email_contacts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('TManager.uid'), nullable=False)
    contact_email = db.Column(db.String(256), nullable=False)
    contact_name = db.Column(db.String(256), nullable=True)
    level = db.Column(db.Integer, default=0)
    last_interaction_at = db.Column(db.DateTime, nullable=True)
    inbound_count = db.Column(db.Integer, default=0)
    outbound_count = db.Column(db.Integer, default=0)
    last_subject = db.Column(db.Text, nullable=True)
    last_subjects_json = db.Column(db.Text, nullable=True)
    first_interaction_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'contact_email', name='uq_user_contact'),
        db.Index('ix_user_contact_email', 'user_id', 'contact_email'),
    )
