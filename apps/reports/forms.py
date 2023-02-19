# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - 龍骨王
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Email, DataRequired

# 記錄各式規格

class ModifyEventForm():

    #我們這邊誰發起或是負責這項活動。
    #這次有哪些客戶參與
    def __init__(self,value):
        self.activityid=""
        self.description=""    
        self.nextstep=""    
        

        if 'activityid' in value:
            self.activityid=value['activityid']
        if 'description' in value:
            self.description=value['description']    
        if 'nextstep' in value:
            self.nextstep=value['nextstep']    
        
