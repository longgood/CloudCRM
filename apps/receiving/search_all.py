from email.utils import getaddresses
from tqdm import tqdm
import re, os, pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

SCOPES           = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = '../client_secret_…apps.googleusercontent.com.json'
TOKEN_FILE       = 'token.pickle'

# —————————————————————————————
# 1. AUTHENTICATE & BUILD SERVICE
# —————————————————————————————
creds = None
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)

service = build('gmail', 'v1', credentials=creds)

# —————————————————————————————
# 2. HELPER FUNCTIONS
# —————————————————————————————
def list_message_ids(label_ids=None, query=None):
    ids, page_token = [], None
    while True:
        resp = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            q=query,
            pageToken=page_token,
            maxResults=500
        ).execute()
        ids.extend(m['id'] for m in resp.get('messages', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return ids

def get_message_metadata(msg_id):
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

    hdrs = {h['name']: h['value']
            for h in msg.get('payload',{}).get('headers',[])}
    hdrs['threadId'] = msg.get('threadId')
    return hdrs

def collect_sg_recipients(hdrs):
    """Return list of (name,email) for every .sg address in From/To/Cc/Bcc."""
    addrs = getaddresses([
        hdrs.get('From',''),
        hdrs.get('To',''),
        hdrs.get('Cc',''),
        hdrs.get('Bcc','')
    ])
    return [
        (name.strip().strip('"'), email_addr)
        for name, email_addr in addrs
        if email_addr.lower().endswith('.sg')
    ]

# —————————————————————————————
# 3. PREPARE YOUR “CRM” DICT
# —————————————————————————————
# We'll store per‐customer:
#   'name'           (first seen)
#   'sent_threads'   (set of threadIds where *you* sent to .sg)
#   'cc_threads'     (set of threadIds where *you* were cc'd alongside .sg addrs)
customers = {}

# —————————————————————————————
# 4. SCAN YOUR SENT MAIL FOR .sg RECIPIENTS
# —————————————————————————————
sent_ids = list_message_ids(label_ids=['SENT'], query='to:.sg')
print(f"🔍 Found {len(sent_ids)} Sent messages to .sg addresses")

for msg_id in tqdm(sent_ids, desc="Scanning Sent → .sg"):
    hdrs = get_message_metadata(msg_id)
    if not hdrs:
        continue
    for name, email_addr in collect_sg_recipients(hdrs):
        info = customers.setdefault(email_addr, {
            'name': name,
            'sent_threads': set(),
            'cc_threads': set()
        })
        info['sent_threads'].add(hdrs['threadId'])

# —————————————————————————————
# 5. SCAN YOUR INBOX FOR MESSAGES WHERE *YOU* ARE CC’D
# —————————————————————————————
# 5a. First, fetch your own email address
profile = service.users().getProfile(userId='me').execute()
me = profile['emailAddress']
print(f"ℹ️ Scanning INBOX for cc:{me}")

# 5b. List every message where you were cc'd
cc_ids = list_message_ids(label_ids=['INBOX'], query=f'cc:{me}')
print(f"🔍 Found {len(cc_ids)} INBOX messages where you were CC’d")

for msg_id in tqdm(cc_ids, desc="Scanning INBOX → cc:me"):
    hdrs = get_message_metadata(msg_id)
    if not hdrs:
        continue
    # from these, only care about any .sg addresses in the thread
    for name, email_addr in collect_sg_recipients(hdrs):
        info = customers.setdefault(email_addr, {
            'name': name,
            'sent_threads': set(),
            'cc_threads': set()
        })
        info['cc_threads'].add(hdrs['threadId'])

# —————————————————————————————
# 6. REVIEW YOUR RESULTS
# —————————————————————————————
for email, info in customers.items():
    print(f"{email:30} {info['name']:20}  sent: {len(info['sent_threads']):4}  cc: {len(info['cc_threads']):4}")
