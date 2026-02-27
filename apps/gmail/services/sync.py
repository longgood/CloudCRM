# -*- encoding: utf-8 -*-

import datetime
import json
import logging
from email.utils import getaddresses, parseaddr

from apps import db
from apps.gmail.models import GmailAccount, EmailMessage
from apps.gmail.services.oauth import build_gmail_service

logger = logging.getLogger(__name__)


def parse_email_addresses(header_value):
    """Parse email header into list of lowercase email addresses."""
    if not header_value:
        return []
    pairs = getaddresses([header_value])
    return [email.lower().strip() for name, email in pairs if email]


def parse_display_name(header_value):
    """Get the first display name from an email header."""
    if not header_value:
        return None
    pairs = getaddresses([header_value])
    for name, email in pairs:
        if name:
            return name.strip().strip('"')
    return None


def paginated_list_messages(service, query, label_ids=None):
    """Paginate through Gmail messages.list results. Returns list of message dicts with 'id'."""
    ids = []
    page_token = None
    while True:
        kwargs = {
            'userId': 'me',
            'q': query,
            'pageToken': page_token,
            'maxResults': 500
        }
        if label_ids:
            kwargs['labelIds'] = label_ids
        resp = service.users().messages().list(**kwargs).execute()
        msgs = resp.get('messages', [])
        ids.extend(m['id'] for m in msgs)
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return ids


def fetch_message_metadata(service, msg_id):
    """Fetch a single message's metadata from Gmail API."""
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='metadata',
        metadataHeaders=['From', 'To', 'Cc', 'Subject']
    ).execute()
    return msg


def sync_gmail(user_id, days=365):
    """
    Sync Gmail messages for a user.
    Returns the number of new messages processed.
    """
    gmail_account = GmailAccount.query.filter_by(user_id=user_id).first()
    if not gmail_account:
        raise ValueError("No Gmail account connected for this user.")

    service = build_gmail_service(gmail_account)

    # Get user's own email
    profile = service.users().getProfile(userId='me').execute()
    my_email = profile['emailAddress'].lower()
    logger.info(f"Syncing Gmail for {my_email}, last {days} days")

    # Build queries to exclude promotions and social
    base_filter = f"newer_than:{days}d -category:promotions -category:social"

    # Fetch outbound message IDs
    outbound_query = f"from:me {base_filter}"
    outbound_ids = paginated_list_messages(service, outbound_query)
    logger.info(f"Found {len(outbound_ids)} outbound messages")

    # Fetch inbound message IDs
    inbound_query = f"to:me {base_filter}"
    inbound_ids = paginated_list_messages(service, inbound_query)
    logger.info(f"Found {len(inbound_ids)} inbound messages")

    # Combine and deduplicate
    all_ids = list(dict.fromkeys(outbound_ids + inbound_ids))
    logger.info(f"Total unique messages: {len(all_ids)}")

    # Get existing message IDs to skip
    existing_ids = set(
        row[0] for row in
        db.session.query(EmailMessage.message_id)
        .filter_by(user_id=user_id)
        .all()
    )

    new_ids = [mid for mid in all_ids if mid not in existing_ids]
    logger.info(f"New messages to fetch: {len(new_ids)}")

    processed = 0
    batch_size = 100

    for i, msg_id in enumerate(new_ids):
        try:
            msg = fetch_message_metadata(service, msg_id)
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}

            from_email = parse_email_addresses(headers.get('From', ''))[0] if parse_email_addresses(headers.get('From', '')) else ''
            to_emails = parse_email_addresses(headers.get('To', ''))
            cc_emails = parse_email_addresses(headers.get('Cc', ''))
            subject = headers.get('Subject', '')
            snippet = msg.get('snippet', '')
            thread_id = msg.get('threadId', '')
            label_ids = msg.get('labelIds', [])

            # Convert internalDate (ms since epoch) to datetime
            internal_date_ms = int(msg.get('internalDate', 0))
            internal_date = datetime.datetime.utcfromtimestamp(internal_date_ms / 1000)

            # Determine direction
            direction = 'outbound' if from_email == my_email else 'inbound'

            email_msg = EmailMessage(
                user_id=user_id,
                message_id=msg_id,
                thread_id=thread_id,
                from_email=from_email,
                to_emails=json.dumps(to_emails),
                cc_emails=json.dumps(cc_emails),
                subject=subject,
                snippet=snippet,
                internal_date=internal_date,
                labels=json.dumps(label_ids),
                direction=direction
            )
            db.session.add(email_msg)
            processed += 1

            # Batch commit
            if processed % batch_size == 0:
                db.session.commit()
                logger.info(f"Committed {processed}/{len(new_ids)} messages")

        except Exception as e:
            logger.warning(f"Error processing message {msg_id}: {e}")
            continue

    # Final commit
    db.session.commit()

    # Update last sync time
    gmail_account.last_sync_at = datetime.datetime.utcnow()
    db.session.commit()

    logger.info(f"Sync complete. Processed {processed} new messages.")

    # Run contact aggregation
    from apps.gmail.services.level import aggregate_contacts
    aggregate_contacts(user_id, my_email)

    return processed
