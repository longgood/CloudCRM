# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - 龍骨王
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Email, DataRequired

# 記錄各式規格

class CreateActivityForm():

    #我們這邊誰發起或是負責這項活動。
    #這次有哪些客戶參與
    def __init__(self,value):
        self.facility_name=""
        self.customer_name=""
        self.customer_title=""
        self.starttime=""
        self.endtime=""
        self.type=0  
        self.description=""    
        self.nextstep=""    
        self.recommand=""    

        
        if 'facility_name' in value:
            self.facility_name=value['facility_name']
        if 'customer_name' in value:
            self.customer_name=value['customer_name']
        if 'customer_title' in value:
            self.customer_title=value['customer_title']
        
        if 'starttime' in value:
            self.starttime=value['starttime']
        if 'endtime' in value:
            self.endtime=value['endtime']
        if 'type' in value:
            self.type=value['type']    
        if 'description' in value:
            self.description=value['description']    
        if 'nextstep' in value:
            self.nextstep=value['nextstep']    
        if 'recommand' in value:
            self.recommand=value['recommand']    

    """
    ownerid=StringField('owner',id='owner_create',validators=[DataRequired()])
    
    starttime=StringField('StartTime',id='starttime_create')
    endtime=StringField('EndTime',id='endtime_create')
    #甚麼樣類型的拜訪，0寫信，1.LINE，2.十分鐘內的通話，3.30分鐘的通話，4.會面半小時，5.面對面三人以上會議
    type=StringField('type',id='type_create')
    description=StringField('Description',id='description_create')
    nextstep=StringField('NextStep',id='nextstep_create')
    #supervisor的建議。
    recommand=StringField('Recommand',id='recommand_create')
    """
    
    
    
    
    """
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

    """
class CreateFacilityForm(FlaskForm):
    name  =StringField('Name',id='name_create',validators=[DataRequired()])
    address = StringField('Address',
                      id='address_create',
                      validators=[DataRequired()])


class CreateCustomerForm(FlaskForm):


    """
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
    """


    