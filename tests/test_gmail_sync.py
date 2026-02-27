# -*- encoding: utf-8 -*-

"""Integration tests for Gmail sync with mocked Gmail API."""

import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from apps.gmail.models import GmailAccount, EmailMessage, EmailContact
from apps.gmail.services.crypto import encrypt_token, decrypt_token


def test_crypto_roundtrip(app_context, db):
    """Test that token encryption/decryption is reversible."""
    original = "my-secret-refresh-token-12345"
    encrypted = encrypt_token(original)
    assert encrypted != original
    decrypted = decrypt_token(encrypted)
    assert decrypted == original


def test_gmail_account_creation(app_context, db):
    """Test creating a GmailAccount record."""
    encrypted = encrypt_token("fake-refresh-token")
    account = GmailAccount(
        user_id=1,
        google_email="test@gmail.com",
        encrypted_refresh_token=encrypted,
        scopes="https://www.googleapis.com/auth/gmail.readonly"
    )
    db.session.add(account)
    db.session.commit()

    found = GmailAccount.query.filter_by(user_id=1).first()
    assert found is not None
    assert found.google_email == "test@gmail.com"
    assert decrypt_token(found.encrypted_refresh_token) == "fake-refresh-token"


def test_email_message_uniqueness(app_context, db):
    """Test that duplicate message_ids for the same user are rejected."""
    msg1 = EmailMessage(
        user_id=1, message_id="msg1", thread_id="t1",
        from_email="a@b.com", subject="Test",
        internal_date=datetime.utcnow(), direction="inbound"
    )
    db.session.add(msg1)
    db.session.commit()

    # Same message_id for same user should fail
    msg2 = EmailMessage(
        user_id=1, message_id="msg1", thread_id="t1",
        from_email="a@b.com", subject="Test dupe",
        internal_date=datetime.utcnow(), direction="inbound"
    )
    db.session.add(msg2)
    try:
        db.session.commit()
        assert False, "Should have raised IntegrityError"
    except Exception:
        db.session.rollback()


def test_email_contact_creation(app_context, db):
    """Test creating and querying EmailContact."""
    contact = EmailContact(
        user_id=1,
        contact_email="john@example.com",
        contact_name="John Doe",
        level=2,
        inbound_count=3,
        outbound_count=5,
        last_interaction_at=datetime.utcnow(),
        last_subject="Re: Meeting next week"
    )
    db.session.add(contact)
    db.session.commit()

    found = EmailContact.query.filter_by(user_id=1, contact_email="john@example.com").first()
    assert found is not None
    assert found.level == 2
    assert found.inbound_count == 3
    assert found.outbound_count == 5


@patch('apps.gmail.services.sync.build_gmail_service')
def test_sync_gmail_stores_messages(mock_build, app_context, db):
    """Test that sync_gmail correctly stores messages and aggregates contacts."""
    from apps.gmail.services.sync import sync_gmail

    # Setup: create a Gmail account
    encrypted = encrypt_token("fake-token")
    account = GmailAccount(
        user_id=1,
        google_email="me@test.com",
        encrypted_refresh_token=encrypted,
        scopes="https://www.googleapis.com/auth/gmail.readonly"
    )
    db.session.add(account)
    db.session.commit()

    # Mock the Gmail service
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Mock getProfile
    mock_service.users().getProfile.return_value.execute.return_value = {
        'emailAddress': 'me@test.com'
    }

    # Mock messages.list - return 2 messages for outbound, 1 for inbound
    # We need to handle two separate list calls (outbound + inbound)
    list_responses = [
        # Outbound response
        {'messages': [{'id': 'msg1'}]},
        # Inbound response
        {'messages': [{'id': 'msg2'}]},
    ]
    mock_service.users().messages().list.return_value.execute.side_effect = list_responses

    # Mock messages.get for each message
    get_responses = [
        {
            'id': 'msg1', 'threadId': 't1',
            'internalDate': '1700000000000',
            'snippet': 'Hello there',
            'labelIds': ['SENT'],
            'payload': {'headers': [
                {'name': 'From', 'value': 'me@test.com'},
                {'name': 'To', 'value': 'contact@example.com'},
                {'name': 'Subject', 'value': 'Hello'},
            ]}
        },
        {
            'id': 'msg2', 'threadId': 't2',
            'internalDate': '1700001000000',
            'snippet': 'Reply from contact',
            'labelIds': ['INBOX'],
            'payload': {'headers': [
                {'name': 'From', 'value': '"Contact Person" <contact@example.com>'},
                {'name': 'To', 'value': 'me@test.com'},
                {'name': 'Subject', 'value': 'Re: Hello'},
            ]}
        },
    ]
    mock_service.users().messages().get.return_value.execute.side_effect = get_responses

    # Run sync
    count = sync_gmail(user_id=1, days=30)

    assert count == 2

    # Check messages stored
    messages = EmailMessage.query.filter_by(user_id=1).all()
    assert len(messages) == 2

    outbound = EmailMessage.query.filter_by(user_id=1, direction='outbound').first()
    assert outbound is not None
    assert outbound.from_email == 'me@test.com'

    inbound = EmailMessage.query.filter_by(user_id=1, direction='inbound').first()
    assert inbound is not None
    assert inbound.from_email == 'contact@example.com'

    # Check contact aggregation
    contact = EmailContact.query.filter_by(user_id=1, contact_email='contact@example.com').first()
    assert contact is not None
    assert contact.level == 1  # bidirectional (1 each way)
    assert contact.inbound_count == 1
    assert contact.outbound_count == 1
