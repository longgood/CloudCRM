# -*- encoding: utf-8 -*-

import datetime
import json
import logging

from apps import db
from apps.gmail.models import EmailMessage, EmailContact
from apps.gmail.services.sync import parse_display_name

logger = logging.getLogger(__name__)


def calculate_level(inbound_count, outbound_count, last_interaction_at, now=None):
    """
    Calculate contact interaction level.

    Level 0: Any interaction (at least 1 in either direction)
    Level 1: Bidirectional (inbound >= 1 AND outbound >= 1)
    Level 2: Stable (inbound >= 2 AND outbound >= 2 AND last interaction within 900 days)
    Level 3: Stable (inbound >= 3 AND outbound >= 3 AND last interaction within 180 days)

    Returns the highest qualifying level, or -1 if no interaction.
    """
    if now is None:
        now = datetime.datetime.utcnow()

    if inbound_count == 0 and outbound_count == 0:
        return -1

    level = 0  # At least 1 in either direction

    if inbound_count >= 1 and outbound_count >= 1:
        level = 1

    if last_interaction_at:
        days_since = (now - last_interaction_at).days

        if inbound_count >= 2 and outbound_count >= 2 and days_since <= 900:
            level = 2

        if inbound_count >= 3 and outbound_count >= 3 and days_since <= 180:
            level = 3

    return level


def aggregate_contacts(user_id, my_email=None):
    """
    Recalculate all email_contacts for a user from email_messages.
    Supports both address-based aggregation.
    """
    now = datetime.datetime.utcnow()

    if my_email is None:
        from apps.gmail.models import GmailAccount
        gmail_account = GmailAccount.query.filter_by(user_id=user_id).first()
        if not gmail_account:
            return
        my_email = gmail_account.google_email.lower()

    logger.info(f"Aggregating contacts for user {user_id} ({my_email})")

    messages = EmailMessage.query.filter_by(user_id=user_id).all()

    contacts_data = {}

    for msg in messages:
        if msg.direction == 'outbound':
            # I sent this - recipients are contacts
            all_recipients = []
            if msg.to_emails:
                try:
                    all_recipients.extend(json.loads(msg.to_emails))
                except (json.JSONDecodeError, TypeError):
                    pass
            if msg.cc_emails:
                try:
                    all_recipients.extend(json.loads(msg.cc_emails))
                except (json.JSONDecodeError, TypeError):
                    pass

            for email in all_recipients:
                email = email.lower().strip()
                if email == my_email or not email:
                    continue
                entry = contacts_data.setdefault(email, _new_entry())
                entry['outbound_count'] += 1
                _update_interaction(entry, msg)

        elif msg.direction == 'inbound':
            # Someone sent to me - the sender is a contact
            sender = msg.from_email.lower().strip()
            if sender == my_email or not sender:
                continue
            entry = contacts_data.setdefault(sender, _new_entry())
            entry['inbound_count'] += 1
            _update_interaction(entry, msg)
            # Capture display name from inbound
            if not entry['name']:
                entry['name'] = parse_display_name(msg.from_email)

    # Calculate levels and upsert contacts
    for email, data in contacts_data.items():
        data['level'] = calculate_level(
            inbound_count=data['inbound_count'],
            outbound_count=data['outbound_count'],
            last_interaction_at=data['last_interaction_at'],
            now=now
        )

        contact = EmailContact.query.filter_by(user_id=user_id, contact_email=email).first()
        if not contact:
            contact = EmailContact(user_id=user_id, contact_email=email)
            db.session.add(contact)

        contact.contact_name = data.get('name')
        contact.level = data['level']
        contact.inbound_count = data['inbound_count']
        contact.outbound_count = data['outbound_count']
        contact.last_interaction_at = data['last_interaction_at']
        contact.first_interaction_at = data.get('first_interaction_at')
        contact.last_subject = data['subjects'][0] if data['subjects'] else None
        contact.last_subjects_json = json.dumps(data['subjects'][:3], ensure_ascii=False)

    db.session.commit()
    logger.info(f"Aggregated {len(contacts_data)} contacts for user {user_id}")


def _new_entry():
    return {
        'inbound_count': 0,
        'outbound_count': 0,
        'last_interaction_at': None,
        'first_interaction_at': None,
        'subjects': [],
        'name': None
    }


def _update_interaction(entry, msg):
    """Update a contact entry with data from a message."""
    if entry['last_interaction_at'] is None or msg.internal_date > entry['last_interaction_at']:
        entry['last_interaction_at'] = msg.internal_date
    if entry['first_interaction_at'] is None or msg.internal_date < entry['first_interaction_at']:
        entry['first_interaction_at'] = msg.internal_date
    if msg.subject:
        # Insert at front, keep sorted by most recent
        entry['subjects'].insert(0, msg.subject)
        entry['subjects'] = entry['subjects'][:3]
