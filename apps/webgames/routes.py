# -*- encoding: utf-8 -*-

from apps import db
from apps.home import blueprint
from flask import render_template, request,send_file
from flask_login import login_required
from jinja2 import TemplateNotFound
import os

@blueprint.route("/webtest_001")
def webgame001():
    return render_template('webgames/001.html')
    #return render_template('report/download.html')
