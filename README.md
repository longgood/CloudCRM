客戶管理系統 CloudCRM
--

## Quick Start

```bash
# 1. Create virtualenv and install dependencies
virtualenv env && source env/Scripts/activate
pip install -r requirements.txt

# 2. Configure environment variables (see .env file)
# 3. Run the app
python run.py
```

## Environment Variables

Edit `.env` to configure:

```env
# Existing
DEBUG=True
SECRET_KEY=your-secret-key

# Google OAuth (for Gmail API) - Required for Gmail features
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost/gmail/callback

# Token encryption - Required for Gmail features
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY=your-fernet-key

# OpenAI - Required for business card extraction + email draft generation
OPENAI_API_KEY=sk-your-key

# Tesseract OCR path (Windows)
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe

# Business card upload directory
UPLOAD_FOLDER_NAMECARD=D:/testdata/namecard

# Company intro for email drafts
COMPANY_INTRO_TEMPLATE=Your company introduction here...
```

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable the **Gmail API**
4. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized redirect URIs: `http://localhost/gmail/callback` (dev) and your production URL
7. Copy the **Client ID** and **Client Secret** to `.env`
8. Configure the OAuth consent screen with scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`

## New Features (v2.0)

### A) Gmail Email Contacts
- Connect Gmail via OAuth
- Sync email messages (exclude promotions/social)
- Auto-calculate interaction levels:
  - **Level 0**: Any contact (1+ email either direction)
  - **Level 1**: Bidirectional (1+ each way)
  - **Level 2**: Stable (2+ each way, within 900 days)
  - **Level 3**: Active (3+ each way, within 180 days)
- Filter/search contacts by level, email, name
- Routes: `/gmail/connect`, `/gmail/contacts`, `/gmail/sync`

### B) Business Card Processing
- Upload business card image (JPG/PNG)
- OCR text extraction (Tesseract)
- LLM-powered structured data extraction (OpenAI)
- Generate personalized email draft
- Send via Gmail API
- Routes: `/namecard/upload`, `/namecard/cards`, `/namecard/draft`, `/namecard/send`

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
apps/
  authentication/   # Login, models (TManager, TUser, TFacility, etc.)
  home/             # Dashboard
  customer/         # Customer management
  reports/          # Reports
  gmail/            # [NEW] Gmail OAuth, sync, contacts
  namecard/         # [NEW] Business card upload, OCR, draft, send
  templates/        # Jinja2 templates
  static/           # CSS, JS, images (Volt Dashboard)
```
