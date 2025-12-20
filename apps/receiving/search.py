from email import message_from_bytes
from email.utils import getaddresses

import re
import os
import pickle
from tqdm import tqdm
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

SCOPES          = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE= '../client_secret_231388179835-…apps.googleusercontent.com.json'
TOKEN_FILE      = 'token.pickle'

# —————————————————————————————————————————————
# 1. Authenticate & build the Gmail service
# —————————————————————————————————————————————
creds = None
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)


# —————————————————————————————————————————————
# 2. Helpers: pagination + SG‐check + metadata fetch
# —————————————————————————————————————————————
def list_message_ids(label_ids=None, query=None):
    ids = []
    page_token = None

    while True:
        resp = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            q=query,
            pageToken=page_token,
            maxResults=500    # per‑page cap (Gmail’s hard limit)
        ).execute()

        ids.extend(m['id'] for m in resp.get('messages', []))

        page_token = resp.get('nextPageToken')
        if not page_token:
            break

    return ids
"""
def list_message_ids(label_ids=None, query=None):
    
    ids = []
    page_token = None
    while True:
        resp = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            q=query,
            pageToken=page_token,
            maxResults=500
        ).execute()
        msgs = resp.get('messages', [])
        ids.extend(m['id'] for m in msgs)
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return ids
"""

def get_message_metadata(msg_id):
    """Fetch From/To/Cc/Bcc headers + threadId."""
    try:
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['From','To','Cc','Bcc']
        ).execute()
    except HttpError as e:
        print(f"⚠️ Skipping {msg_id}: {e}")
        return None

    hdrs = { h['name']: h['value']
             for h in msg.get('payload',{}).get('headers',[]) }
    hdrs['threadId'] = msg.get('threadId')
    return hdrs

def collect_sg_recipients(hdrs):
    """Return list of (name,email) for every .sg address in From/To/Cc/Bcc."""
    addr_strs = [
        hdrs.get('From',''),
        hdrs.get('To',''),
        hdrs.get('Cc',''),
        hdrs.get('Bcc','')
    ]
    all_addrs = getaddresses(addr_strs)
    return [
        (name.strip().strip('"'), email_addr)
        for name, email_addr in all_addrs
        if email_addr.lower().endswith('.sg')
    ]



def is_sg_address(addr):
    return bool(re.search(r'@[^>]+\.sg\b', addr, re.IGNORECASE))

def get_message_metadata(msg_id):
    """Fetch only the From/To headers + threadId."""
    try:
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['From','To']
        ).execute()
    except HttpError as e:
        print(f"⚠️ Skipping metadata for {msg_id}: {e}")
        return None

    hdrs = { h['name']: h['value']
             for h in msg.get('payload',{}).get('headers',[]) }
    hdrs['threadId'] = msg.get('threadId')
    return hdrs


# —————————————————————————————————————————————
# 3. Fetch *all* Sent‐folder IDs with a .sg recipient
# —————————————————————————————————————————————
sg_query = 'to:.sg'  
sent_ids = list_message_ids(label_ids=['SENT'], query=sg_query)
print(f"Found {len(sent_ids)} Sent messages addressed to .sg")

# —————————————————————————————————————————————
# 4. Scan & build your “CRM” dict
# —————————————————————————————————————————————
customers = {}
for msg_id in tqdm(sent_ids, desc="Scanning Sent → .sg"):
    hdrs = get_message_metadata(msg_id)
    if not hdrs:
        continue

    for name, email_addr in collect_sg_recipients(hdrs):
        info = customers.setdefault(email_addr, {
            'name': name or hdrs.get('From',''),
            'thread_ids': set()
        })
        info['thread_ids'].add(hdrs['threadId'])

# —————————————————————————————————————————————
# 5. Inspect results
# —————————————————————————————————————————————
for email, info in customers.items():
    print(f"{email:30}  {info['name']:20}  threads: {len(info['thread_ids'])}")
