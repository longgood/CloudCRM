# -*- encoding: utf-8 -*-

import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def create_message(sender, to, subject, body_text, body_html=None):
    """Create an RFC 2822 message, base64url-encoded for Gmail API."""
    if body_html:
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))
    else:
        msg = MIMEText(body_text, 'plain', 'utf-8')

    msg['to'] = to
    msg['from'] = sender
    msg['subject'] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}


def send_message(service, message):
    """Send a message via Gmail API. Returns the sent message resource."""
    logger.info(f"Sending email via Gmail API")
    result = service.users().messages().send(userId='me', body=message).execute()
    logger.info(f"Email sent. Message ID: {result.get('id')}")
    return result
