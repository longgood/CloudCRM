# -*- encoding: utf-8 -*-


#from apps import db
from apps import db
from apps.customer.datas import TCustomerDataFake
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
data=TCustomerDataFake()


def get_id(num):
    pre=random.randint(10,99)
    id=pre*10000000+num
    return id
@blueprint.route('/customer_activity_test')
def customer_activity_test():
    
    fac=TFacility.query.all()
    for f in fac:
        print("機構:",f)
    
    print("------")
    cust=TCustomer.query.all()
    for c in cust:
        print("使用者:",c)
    
    return "hello"+str(datetime.now().time())
@blueprint.route('/customer_activity',methods=['GET', 'POST'])
@login_required
def customer_activity():
    activity_form = CreateActivityForm(request.form)
    msg=None
    if 'register' in request.form:
        facilityname=activity_form.facility_name
        customername=activity_form.customer_name
        title=activity_form.customer_title
        facility = TFacility.query.filter_by(name=facilityname).first()


        starttime=datetime.strptime(activity_form.starttime, "%Y-%m-%dT%H:%M")
        
        
        

        if not facility:
            fac=TFacility()
            fac.id=get_id(TFacility.query.count())
            fac.name=facilityname
            db.session.add(fac)
            facilityid=fac.id
            print(facilityname,"已經新建立!",fac)
        else:
            facilityid=facility.id
            print(facilityname+"的資料已經存在資料庫內")
        customer = TCustomer.query.filter_by(name=customername,title=title).first()
        if not customer:
            cust=TCustomer()
            cust.id=get_id(TCustomer.query.count())
            cust.name=customername
            cust.title=title
            cust.facilityid=facilityid
            db.session.add(cust)
            print(customername,"已經新增!",cust)
        else:
            print(customername+title+"的資料已經存在資料庫內!")
        print("--------------------------------------------------")
        act=TActivity()
        print("--------------------------------------------------")
        id=get_id(TActivity.query.count())
        print("--------------------------------------------------")
        print("id:",id)
        act.id=id
        
        act.ownerid="ifeellike"
        act.facilityid=activity_form.facility_name
        act.customerList=act.customerList+activity_form.customer_name+";321"#customer.id
        act.starttime=starttime
        delta = timedelta(days=2)
        act.endtime=delta+starttime
        act.type=0
        act.description=activity_form.description
        act.nextstep=activity_form.nextstep
        act.recommand=""
        print("活動內容:",act)
        #supervisor的建議。

        db.session.add(act)    
        db.session.commit()
        msg=facilityname+customername+title+"新的拜訪資料已經建立!"
        
    print("現在:",datetime.now().time())
    return render_template('customer/add_new_activity.html', form=activity_form,msg=msg)
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
@blueprint.route('/customer_search',methods=['GET'])
@login_required
def customer_search():
    keyword = request.args.get('keyword')
    
    data=TFacility.query.filter_by(name=keyword).all()
    result=""
    print("search",data)
    for r in data:
        result=result+r.name+"#"
        
    print("result",result)
    return result