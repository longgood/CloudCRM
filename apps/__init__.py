# -*- encoding: utf-8 -*-


import json

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
    for module_name in ('authentication', 'home','reports','customer','webgames','gmail','namecard'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    # Import all models so db.create_all() discovers them
    import apps.authentication.models
    import apps.gmail.models
    import apps.namecard.models

    # Flask 2.3+ removed before_first_request; use compatible approach
    _db_initialized = False

    if hasattr(app, 'before_first_request'):
        @app.before_first_request
        def initialize_database():
            db.create_all()
    else:
        @app.before_request
        def initialize_database():
            nonlocal _db_initialized
            if not _db_initialized:
                db.create_all()
                _db_initialized = True

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def get_locale():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    return request.accept_languages.best_match(['zh', 'en', 'ja'])

def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Flask-Babel 4.0+ uses constructor params; older versions use decorators
    try:
        babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)
    except TypeError:
        babel = Babel(app)
        babel.localeselector(get_locale)
        babel.timezoneselector(get_timezone)

    register_extensions(app)
    register_blueprints(app)
    configure_database(app)

    # Custom Jinja2 filter for JSON parsing in templates
    def from_json(value):
        try:
            return json.loads(value) if value else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    app.jinja_env.filters['from_json'] = from_json

    return app
    