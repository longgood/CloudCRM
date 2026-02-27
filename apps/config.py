# -*- encoding: utf-8 -*-


import os

from decouple import config

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='321ES#p%reAA_009AC') #SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')
    LANGUAGES = ['en', 'zh','ja','fr']
    POOL_SIZE=20
    MAX_OVERFLOW=0
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    # This will create a file in <app> FOLDER
    
    
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'longgooddb.bytes')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'D:/testdata'
    static_folder="./"
    template_folder="./"

    # Google OAuth (for Gmail API)
    GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
    GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
    GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='http://localhost/gmail/callback')

    # Fernet encryption key for OAuth tokens
    FERNET_KEY = config('FERNET_KEY', default='')

    # OpenAI API key (for business card extraction + draft generation)
    OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

    # Tesseract OCR path
    TESSERACT_CMD = config('TESSERACT_CMD', default='tesseract')

    # Upload directory for business card images
    UPLOAD_FOLDER_NAMECARD = config('UPLOAD_FOLDER_NAMECARD', default=os.path.join(basedir, '..', 'data', 'namecard'))

    # Company introduction template for draft generation
    COMPANY_INTRO_TEMPLATE = config('COMPANY_INTRO_TEMPLATE', default='')
    

class ProductionConfig(Config):
    print("--ProductionConfig--")
    DEBUG = False
    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    """
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE', default='mysql'),
        config('DB_USERNAME', default='***'),
        config('DB_PASS', default='***'),
        config('DB_HOST', default='**'),
        config('DB_PORT', default=3306),
        config('DB_NAME', default='dbtest')
    )
    """
class DebugConfig(Config):
    print("--DebugConfig--")
    DEBUG = True
    
    basedir = os.path.abspath(os.path.dirname(__file__))

    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'longgooddb.bytes')
    
    
    
# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
