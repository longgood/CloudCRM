# -*- encoding: utf-8 -*-

import os
import pytest
from cryptography.fernet import Fernet

# Set test env vars before app import
os.environ['GOOGLE_CLIENT_ID'] = 'test-client-id'
os.environ['GOOGLE_CLIENT_SECRET'] = 'test-client-secret'
os.environ['GOOGLE_REDIRECT_URI'] = 'http://localhost/gmail/callback'
os.environ['FERNET_KEY'] = Fernet.generate_key().decode()
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['TESSERACT_CMD'] = 'tesseract'

from apps import create_app, db as _db
from apps.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'
    GOOGLE_CLIENT_ID = 'test-client-id'
    GOOGLE_CLIENT_SECRET = 'test-client-secret'
    GOOGLE_REDIRECT_URI = 'http://localhost/gmail/callback'
    FERNET_KEY = os.environ['FERNET_KEY']
    OPENAI_API_KEY = 'test-key'
    TESSERACT_CMD = 'tesseract'
    UPLOAD_FOLDER_NAMECARD = '/tmp/test_namecard'
    COMPANY_INTRO_TEMPLATE = 'Test company intro.'


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app
