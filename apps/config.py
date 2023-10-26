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
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE', default='mysql'),
        config('DB_USERNAME', default='longgoodapi'),
        config('DB_PASS', default='ji3cl3gj94MM'),
        config('DB_HOST', default='13.215.160.174'),
        config('DB_PORT', default=3306),
        config('DB_NAME', default='dbtest')
    )
class DebugConfig(Config):
    print("--DebugConfig--")
    DEBUG = True
    
    basedir = os.path.abspath(os.path.dirname(__file__))

    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'longgooddb.bytes')
    
    """
    username="crmweb" #'3.1.154.25'
    password="54158175CRM"
    hostip="18.142.186.21"
    db_name="rehabilitation"
    isLocal=True
    
    
    
    
    #username="cloudapi" #'3.1.154.25'
    #password="54158175LG"
        
        #jp
    port=12105
    hostip="0.tcp.jp.ngrok.io"
    
    
    if isLocal:
            username="root"
            password="rraayy"

            #username="crmweb" #'3.1.154.25'
            #password="54158175CRM"
            hostip="localhost"
            db_name="rehabilitation"
    
    SQLALCHEMY_DATABASE_URI='{}://{}:{}@{}:{}/{}'.format(
        'mysql',
        username,
        password,
        hostip,
        3306,
        db_name)
    """

    
    
# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
