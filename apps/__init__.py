# -*- encoding: utf-8 -*-


from flask import *
from flask_babel import *
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home','reports','customer','webgames','namecard'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    babel = Babel(app)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    
    @babel.localeselector
    def get_locale():
        # if a user is logged in, use the locale from the user settings
        user = getattr(g, 'user', None)
        if user is not None:
            return user.locale
        # otherwise try to guess the language from the user accept
        # header the browser transmits.  We support de/fr/en in this
        # example.  The best match wins.
        return request.accept_languages.best_match(['zh', 'en', 'ja'])
    @babel.timezoneselector
    def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone

    return app
    