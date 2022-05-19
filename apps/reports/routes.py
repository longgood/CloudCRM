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
@blueprint.route('/reports_recovery')
@login_required
def reports_recovery():
    data.report_recovery()
    return ""

@blueprint.route('/reports')
@login_required
def reports():
    username=request.args.get('username')
    return render_template('home/report_general.html',
                            username=username,
                            patientlist=['陳阿帥','妳阿笨','天天才'])
@blueprint.route('/report_general',methods=['GET'])
@login_required
def report_general():
    usermanager=current_user
    
    #取得目前所有使用者資訊
    activityid=request.args.get('activityid')
    isdelete=request.args.get('isdelete')
    #在檢視單人時，會有刪除的選項。
    if isdelete:
        data.hide_activity(activityid)
        print("isdelete",isdelete,",data:",activityid)
        activityid=None
    
    return data.get_report_general(usermanager)
    

@blueprint.route('/report_weekly')
@login_required
def report_weekly():    
    usermanager=current_user
    return data.get_report_weekly(usermanager)
@blueprint.route('/report_follow')
@login_required
def report_follow():    
    usermanager=current_user
    return data.get_report_follow(usermanager)
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
 
