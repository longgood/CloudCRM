# -*- encoding: utf-8 -*-


#from apps import db

from apps.reports.datas import TData

"""
龍骨王股份有限公司
"""

from apps.reports import blueprint
from flask import render_template, redirect, url_for,request
from flask_login import (
    login_required,
    current_user
)
data=TData()
@blueprint.route('/reports')
@login_required
def reports():
    username=request.args.get('username')
    return render_template('home/report_general.html',
                            username=username,
                            patientlist=['陳阿帥','妳阿笨','天天才'])
@blueprint.route('/report_general')
@login_required
def report_general():

    usermanager=current_user
    acts=data.get_activity()
    fac=data.get_facility()
    cust=data.get_customer()
    return render_template('report/report_general.html',activity=acts,facility=fac,customer=cust)

@blueprint.route('/report_history')
@login_required
def report_history():
    patientid=request.args.get('patientid')
    return data.get_history_activity(patientid)
    
@blueprint.route('/report_single')
@login_required
def report_single():
    patientid=request.args.get('patientid')
    return data.get_single_activity(patientid)
@blueprint.route('/user_list')
@login_required
def user_list():
    return render_template('home/user_list.html')
 
@blueprint.route('/skeleton')
@login_required
def user_skeleton():
    return render_template('home/skeleton.html')
    
    
    
@blueprint.route('/skel-<template>')
@login_required
def user_cust_skeleton(template):
    activityid="\"static/skeleton/"+template+".csv.lzma.bvh\""
    print("activityid:",activityid)
    return render_template('home/report_skeleton.html',
                                              activityid=activityid
                                              )