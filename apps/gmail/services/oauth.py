# -*- encoding: utf-8 -*-

import logging
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest
from googleapiclient.discovery import build
from flask import current_app

from apps.gmail.services.crypto import decrypt_token

logger = logging.getLogger(__name__)

SCOPES_READONLY = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES_SEND = ['https://www.googleapis.com/auth/gmail.send']
SCOPES_ALL = SCOPES_READONLY + SCOPES_SEND


def _client_config():
    """Build OAuth client config from environment variables."""
    return {
        "web": {
            "client_id": current_app.config['GOOGLE_CLIENT_ID'],
            "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [current_app.config['GOOGLE_REDIRECT_URI']],
        }
    }


def create_flow(scopes=None):
    """Create a web-server OAuth flow."""
    flow = Flow.from_client_config(
        _client_config(),
        scopes=scopes or SCOPES_ALL,
        redirect_uri=current_app.config['GOOGLE_REDIRECT_URI']
    )
    return flow


def get_authorization_url(scopes=None):
    """Return (url, state) for redirecting the user to Google consent screen."""
    flow = create_flow(scopes)
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url, state


def exchange_code(code, state, scopes=None):
    """Exchange the authorization code for credentials."""
    flow = create_flow(scopes)
    flow.fetch_token(code=code)
    return flow.credentials


def build_gmail_service(gmail_account):
    """Build a Gmail API service from a stored GmailAccount record."""
    refresh_token = decrypt_token(gmail_account.encrypted_refresh_token)
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=current_app.config['GOOGLE_CLIENT_ID'],
        client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
        scopes=gmail_account.scopes.split(',') if gmail_account.scopes else SCOPES_ALL
    )
    if not creds.valid:
        creds.refresh(GoogleAuthRequest())
    return build('gmail', 'v1', credentials=creds)
