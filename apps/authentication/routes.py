# -*- encoding: utf-8 -*-
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import TManager
from apps.authentication.util import verify_pass
from apps.authentication.fakedata import fake
from apps.authentication.util import hash_pass
@blueprint.route('/renew_pswd')
def renew_pswd():
    user=TManager.query.first()
    print(user.password)
    user.password=hash_pass("rraayy")
    db.session.flush()
    db.session.commit()
    print(user.password)
    return "done"
def fake_data():
    result=fake()
    return result.get_test()
@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))
# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    
    login_form = LoginForm(request.form)
    
    if 'login' in request.form:

        # read form data
        userid = request.form['userid']
        password = request.form['password']

        # Locate user
        user=TManager({})
        print("UserID:",userid)
        user=TManager.query.filter(TManager.accountId==userid).first()
        print("right")

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='帳號或是密碼錯誤',
                               form=login_form)
    print("-----CurrentUser:",current_user)
    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))
@blueprint.route('/register_user', methods=['GET', 'POST'])
def register_user():
    create_account_form = CreateAccountForm(request.form)
    for r in request.form:
        print("current",r)
    if 'register' in request.form:

        userid = request.form['userid']
        email = request.form['email']
        password=request.form['password']
        
        realname=request.form['realname']
        jobtitle=request.form['jobtitle']
        
        data={}
        data["eMail"]=email
        data["password"]=password
        data["accountId"]=userid
        data["realName"]=realname
        data["jobTitle"]=jobtitle
        print("---check--",userid,email,password,realname,jobtitle)
        user = TManager.query.filter_by(accountId=userid).first()
        if user:
            print("regiester_manager,userid exist")
            return render_template('accounts/register_user.html',
                                   msg='該帳號名稱已經註冊',
                                   success=False,
                                   form=create_account_form)
        # Check email exists
        #manager = Managers.query.filter_by(email=email).first()
        # else we can create the user
        print("**Form:",request.form)
        print("Dic",data)
        
        user = TManager(data)
        print("user:",user)
        db.session.add(user)
        db.session.commit()
        print("manager, registed:",create_account_form)
        return render_template('accounts/register_user.html',msg=realname+'的帳號'+userid+'已經創立，請<strong>登入<a href="/login"></strong>，或繼續操作新增管理者</a>',
                               success=True,form=create_account_form)
    else:
        return render_template('accounts/register_user.html', form=create_account_form)
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register_manager' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = TManager.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='該帳號名稱已經註冊',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = TManager.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='該郵件已經註冊',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = TManager(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='已經創立，請登入 <a href="/login"></a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)
@blueprint.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    create_account_form = CreateAccountForm(request.form)
    if 'register_patient' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = TManager.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register_patient.html',
                                   msg='該帳號名稱已經註冊',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = TManager.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register_patient.html',
                                   msg='該郵件已經註冊',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = TManager(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register_patient.html',
                               msg='已經創立，請登入 <a href="/login"></a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register_patient.html', form=create_account_form)



@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
