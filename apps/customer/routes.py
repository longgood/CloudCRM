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
    id=pre+num*100+1000000000
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
        day_delta=get_day_delta(activity_form.timedelta)
        minutes_delta=get_minutes_delta(activity_form.minutesdelta)
        type=get_type(activity_form.type)
        print(activity_form.type,"+++++++++++++++++++++++minutes delta",type)
        

        if not facility:
            fac=TFacility()
            fac.id=get_id(TFacility.query.count())
            fac.name=facilityname
            db.session.add(fac)
            facility_id=fac.id
            print(facilityname,"已經新建立!",fac)
        else:
            facility_id=facility.id
            print(facilityname+"的資料已經存在資料庫內")
        customer = TCustomer.query.filter_by(name=customername,title=title).first()
        if not customer:
            customer=TCustomer()
            customer.id=get_id(TCustomer.query.count())
            customer.name=customername
            customer.title=title
            customer.facilityid=facility_id
            db.session.add(customer)
            print(customername,"已經新增!",customer)
            
        else:
            print(customername+title+"的資料已經存在資料庫內!")
        act=TActivity()
        id=get_id(TActivity.query.count())
        print("id:",id)
        act.id=id
        
        act.ownerid="ifeellike"#稍後來測試!
        act.facilityid=facility_id
        act.customerList=str(customer.id)+";"
        act.starttime=starttime
        act.endtime=starttime+timedelta(minutes=minutes_delta)
        
        delta = timedelta(days=day_delta)
        act.nexttime=delta+starttime
        act.type=type
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
def get_type(input):
    result=0
    if input=="寫信":
        result=0
    elif input=="LINE(訊息)":
        result=1
    elif input=="線上通話":
        result=2
    elif input=="會面":
        result=3
    elif input=="面對面三人以上會議":
        result=4
    
    return result
    
def get_minutes_delta(input):
    result=1
    if input=="十分鐘":
        result=10
    elif input=="半小時":
        result=30
    elif input=="一小時":
        result=60
    elif input=="兩小時":
        result=120
    elif input=="四小時":
        result=240
    elif input=="八小時":
        result=480
    return result
def get_day_delta(input):
    result=1
    if input=="兩天後":
        result=2
    elif input=="一周後":
        result=7
    elif input=="兩周後":
        result=14
    elif input=="一個月後":
        result=30
    elif input=="一季(三個月)":
        result=92
    return result
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