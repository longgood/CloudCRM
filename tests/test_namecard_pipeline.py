# -*- encoding: utf-8 -*-

"""Tests for the business card pipeline (OCR, LLM, send)."""

import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from apps.namecard.models import BusinessCard, OutboundDraft
from apps.namecard.services.gmail_send import create_message


def test_business_card_creation(app_context, db):
    """Test creating a BusinessCard record."""
    card = BusinessCard(
        user_id=1,
        image_path="/tmp/test.jpg",
        original_filename="test.jpg",
        ocr_text="John Doe\nCTO\njohn@example.com",
        status="ocr_done"
    )
    db.session.add(card)
    db.session.commit()

    found = BusinessCard.query.filter_by(user_id=1).first()
    assert found is not None
    assert found.original_filename == "test.jpg"
    assert "John Doe" in found.ocr_text


def test_outbound_draft_creation(app_context, db):
    """Test creating an OutboundDraft record."""
    card = BusinessCard(
        user_id=1,
        image_path="/tmp/test.jpg",
        original_filename="test.jpg",
        status="extracted"
    )
    db.session.add(card)
    db.session.commit()

    draft = OutboundDraft(
        user_id=1,
        business_card_id=card.id,
        to_email="john@example.com",
        subject="Nice meeting you",
        body="Dear John, it was great meeting you at the expo.",
        user_prompt="We met at the medical expo",
        status="draft"
    )
    db.session.add(draft)
    db.session.commit()

    found = OutboundDraft.query.filter_by(user_id=1).first()
    assert found is not None
    assert found.to_email == "john@example.com"
    assert found.status == "draft"


def test_create_message_plain_text():
    """Test RFC 2822 message creation for Gmail API."""
    msg = create_message(
        sender="me@test.com",
        to="recipient@test.com",
        subject="Test Subject",
        body_text="Hello, this is a test."
    )
    assert 'raw' in msg
    assert len(msg['raw']) > 0

    # Decode and verify (headers may be lowercase in Python's email lib)
    import base64
    raw_bytes = base64.urlsafe_b64decode(msg['raw'])
    raw_str = raw_bytes.decode('utf-8').lower()
    assert 'to: recipient@test.com' in raw_str
    assert 'subject: test subject' in raw_str


def test_create_message_with_html():
    """Test RFC 2822 message creation with HTML body."""
    msg = create_message(
        sender="me@test.com",
        to="recipient@test.com",
        subject="Test",
        body_text="Plain text",
        body_html="<p>HTML body</p>"
    )
    assert 'raw' in msg

    import base64
    raw_bytes = base64.urlsafe_b64decode(msg['raw'])
    raw_str = raw_bytes.decode('utf-8')
    assert 'multipart/alternative' in raw_str


@patch('apps.namecard.services.ocr.TesseractOCR.extract_text')
def test_ocr_engine(mock_extract):
    """Test OCR engine factory and extraction."""
    from apps.namecard.services.ocr import get_ocr_engine

    mock_extract.return_value = "John Doe\nCTO at Acme\njohn@acme.com"
    engine = get_ocr_engine('tesseract')
    text = engine.extract_text('/fake/path.jpg')
    assert 'John Doe' in text
    assert 'john@acme.com' in text


def test_ocr_engine_invalid_type():
    """Test OCR engine factory with invalid type."""
    from apps.namecard.services.ocr import get_ocr_engine
    import pytest

    with pytest.raises(ValueError, match="Unknown OCR engine"):
        get_ocr_engine('invalid_engine')


@patch('openai.OpenAI')
def test_extract_card_info(mock_openai_cls):
    """Test LLM card info extraction."""
    from apps.namecard.services.llm import extract_card_info

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    expected = {
        "name": "John Doe",
        "title": "CTO",
        "company": "Acme Corp",
        "email": "john@acme.com",
        "phone": "+1234567890",
        "address": None,
        "website": "acme.com",
        "notes": None
    }
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=json.dumps(expected)))
    ]

    result = extract_card_info("John Doe CTO john@acme.com", api_key="fake")
    assert result['name'] == 'John Doe'
    assert result['email'] == 'john@acme.com'
    assert result['company'] == 'Acme Corp'


@patch('openai.OpenAI')
def test_generate_draft(mock_openai_cls):
    """Test LLM draft generation."""
    from apps.namecard.services.llm import generate_draft

    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    expected = {
        "subject": "Nice meeting you at the expo",
        "body": "Dear John,\n\nIt was wonderful meeting you..."
    }
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=json.dumps(expected)))
    ]

    result = generate_draft(
        extracted_json={"name": "John Doe", "company": "Acme"},
        user_prompt="We met at the medical expo",
        company_template="We are LongGood MediTech...",
        api_key="fake"
    )
    assert 'subject' in result
    assert 'body' in result
    assert 'expo' in result['subject'].lower()
