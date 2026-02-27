# -*- encoding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'gmail_blueprint',
    __name__,
    url_prefix='/gmail'
)
