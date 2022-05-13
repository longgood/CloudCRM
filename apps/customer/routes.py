# -*- encoding: utf-8 -*-


#from apps import db
from apps import db
from apps.customer.datas import TCustomerData
from datetime import datetime,timedelta
import time
import random
"""
龍骨王股份有限公司
"""
from apps.customer.forms import CreateFacilityForm,CreateCustomerForm,CreateActivityForm
from apps.authentication.models import TFacility,TActivity,TCustomer
from apps.customer import blueprint
from flask import render_template, redirect, url_for,request
from flask_login import (
    login_required,
    current_user
)
data=TCustomerData()


    
@blueprint.route('/customer_activity',methods=['GET', 'POST'])
@login_required
def customer_activity():
    usermanager=current_user
    activity_form = CreateActivityForm(request.form)
    isregister=False
    if 'register' in request.form:
        isregister=True
    return data.get_customer_activity(activity_form,usermanager,isregister)
    
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
        facility = TFacility.query.filter_by(name=name).first()
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
    
    data=TCustomer.query.filter_by(name=keyword).all()
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
    
    data=TCustomer.query.filter_by(name=keyword).all()
    result=""

    for r in data:
        result=result+r.name+"#"
    print("-------------result----------------",result)
    return result