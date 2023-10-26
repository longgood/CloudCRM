# -*- encoding: utf-8 -*-

from werkzeug.utils import secure_filename
#from apps import db
from apps import db
from apps.customer.datas import TCustomerData
from datetime import datetime,timedelta
import time
import random
"""
龍骨王股份有限公司
"""
from apps.customer.forms import CreateFacilityForm,CreateCustomerForm,CreateEventForm
from apps.authentication.models import TFacility,TEvent,TManager,TCustomer
from apps.customer import blueprint
from flask import render_template, redirect, url_for,request
from flask_login import (
    login_required,
    current_user
)
data=TCustomerData()
@blueprint.route('/customer_followup')
@login_required
def customer_followup():
    print("customer_followup")
    usermanager=current_user
    return data.get_customer_followup(usermanager)
    
@blueprint.route('/customer_activity',methods=['GET', 'POST'])
@login_required
def customer_activity():
    usermanager=current_user
    event_form = CreateEventForm(request.form)
    
    isregister=False
    if 'register' in request.form:
        isregister=True
    return data.get_customer_event(event_form,usermanager,isregister)
@blueprint.route('/customer_activity_adding_mode',methods=['GET', 'POST'])
@login_required
def customer_activity_adding_mode():
    usermanager=current_user
    

    
    activity_form = CreateEventForm(request.form)
    isregister=False
    if 'register' in request.form:
        isregister=True
    return data.get_customer_activity_adding_mode(activity_form,usermanager,isregister)    
@blueprint.route('/customer_customer')
@login_required
def customer_customer():
    return render_template('customer/add_new_customer.html')
@blueprint.route('/customer_facility',methods=['GET', 'POST'])
@login_required
def customer_facility():
    create_facility_form = CreateFacilityForm(request.form)
    if 'register' in request.form:
        
        name = request.form['name']
        address = request.form['address']
        facility = TFacility.query.filter_by(displayName=name).first()
        if facility:
            print("已經存在")
            return render_template('customer/add_new_facility.html',
                                   msg='已有該機構名稱',
                                   success=False,
                                   form=create_facility_form)
        facility = TFacility(**request.form)
        db.session.add(facility)
        db.session.commit()
        return render_template('customer/add_new_facility.html',msg=name+'已經創立，繼續操作新增公司/醫院</a>',
                               success=True,form=create_facility_form)
    else:
        return render_template('customer/add_new_facility.html', form=create_facility_form)
@blueprint.route('/facility_search',methods=['GET'])
@login_required
def facility_search():
    keyword = request.args.get('keyword')
    
    data=TManager.query.filter_by(realName=keyword).all()
    result=""
    print("search",data)
    for r in data:
        result=result+r.name+"#"
    print("-------------result----------------",result)
    return result
@blueprint.route('/customer_search',methods=['GET'])
@login_required
def customer_search():
    keyword = request.args.get('keyword')
    print("名字關鍵字:",keyword)
    data=TManager.query.filter_by(realName=keyword).all()
    result=""

    for r in data:
        result=result+r.name+"#"
    print("-------------result----------------",result)
    return result

@blueprint.route('/register_device',methods=['GET','POST'])
@login_required
def register_device():
    name=None
    if request.method =='POST':
        if request.values['send']=='send':
            if "user" in request.values:
                name=request.values['user']
    return data.get_new_device(name)
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg','JPG', 'jpeg', 'gif','lzma','pdf','json'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
import os         
@blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("upload_file------------",request.method)
    if request.method == 'POST':
        file = request.files['file']
        print("file:",file,",fname:",file.filename)
        print("allow:",allowed_file(file.filename))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("檔案名稱:",filename)
            file.save('e:/test/',filename)
            
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''