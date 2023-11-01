# -*- encoding: utf-8 -*-


import os

from decouple import config

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='321ES#p%reAA_009AC') #SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')
    LANGUAGES = ['en', 'zh','ja','fr']
    
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    # This will create a file in <app> FOLDER
    
    
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'longgooddb.bytes')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'D:/testdata'
    static_folder="./"
    template_folder="./"
    

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
