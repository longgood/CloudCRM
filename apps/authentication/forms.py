# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - 龍骨王
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    userid =  StringField('UserId',
                         id='userid_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):

    print("**在此介紹:",FlaskForm)

    userid  =StringField('UserId',id='userid_create',validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    realname = StringField('Realname',
                         id='realname_create',
                         validators=[DataRequired()])

    jobtitle=StringField('JobTitle',id='jobtitle_create',validators=[DataRequired()])
    