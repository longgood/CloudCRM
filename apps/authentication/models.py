# -*- encoding: utf-8 -*-


from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

#我方的使用者
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id          = db.Column(db.Integer, primary_key=True)
    userid      = db.Column(db.String(64), unique=True)
    email       = db.Column(db.String(64), unique=True)
    password    = db.Column(db.LargeBinary)
    realname    = db.Column(db.String(64))
    jobtitle    = db.Column(db.String(64))
    
    
    #往下管理那些公司內成員
    userList= db.Column(db.String(64))
    #負責的相關客戶
    customerList= db.Column(db.String(64))
    #負責的相關機構
    facilityList= db.Column(db.String(64))
    
    
    #-202301新增(嘗試)
    #boss=db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    #staff=db.relationship("Users",remote_side=[id],backref='Users.boss')#backref=backref("boss",remote_side=[id]))
    #staff=db.relationship("Users",remote_side=[id])#backref=backref("boss",remote_side=[id]))
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    def __repr__(self):
        value="姓名:'%s',id='%s',userid='%s',  職稱:'%s',老闆:'%s',員工:'%s'" % (
                   self.realname,self.id, self.userid, self.jobtitle) 
        
        return value
#每一位顧客或是談話的對象。
class TCustomer(db.Model):
    __tablename__ = 'TCustomer'
    id = db.Column(db.Integer, primary_key=True)
    #我們這邊是由誰建立的
    ownerid=db.Column(db.String(64))
    name = db.Column(db.String(64))
    phone=db.Column(db.String(64))
    cellphone=db.Column(db.String(64))
    lineid=db.Column(db.String(64))
    email = db.Column(db.String(64))
    #每一次相關的活動都會記錄下來。
    activityList=db.Column(db.String(4096))
    #目前所屬的公司
    facilityid=db.Column(db.String(64))
    department = db.Column(db.String(64))    
    title = db.Column(db.String(64))    
    
    submanagers=db.Column(db.String(256))
    
    
    #--202302新增
    fid = db.Column(db.Integer, db.ForeignKey('TFacility.id'))
    
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def check_key(self,dic,key,value=None):
       
        result=None
        try:
            result=dic[key]
        except KeyError:
            result=value
        return result
    def add_new(self,dic=None):
    
        result=False
        if dic:
            id=self.check_key(  dic,"id")
        else:
            id=self.id
        if id is None:
            print("錯誤ID",dic["id"])
            return result
        
        user=TCustomer.query.filter_by(id=id).first()
        if not user:
            if dic:
                self.id             = self.check_key(  dic,"id") 
                self.ownerid        = self.check_key(  dic,"ownerid")  
                self.name           = self.check_key(  dic,"name")  
                self.phone          = self.check_key(  dic,"phone") 
                self.cellphone      = self.check_key(  dic,"cellphone") 
                self.lineid         = self.check_key(  dic,"lineid") 
                self.email          = self.check_key(  dic,"email")  
                self.activityList   = self.check_key(  dic,"activityList")  
                self.facilityid     = self.check_key(  dic,"phone") 
                self.department     = self.check_key(  dic,"department")  
                self.title          = self.check_key(  dic,"title")  
                self.submanagers    = self.check_key(  dic,"submanagers")  
            db.session.add(self)
            db.session.commit()
            result=True
        else:
            print("---重複產出----")
        return result
    def __init__(self):
        return
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    """
    def __repr__(self):
        return "Customer(id='%s', 名稱:'%s', 職稱:'%s',對應的機構:'%s',拜訪:'%s'" % (
                   self.id, self.name, self.title,self.fid,self.visiting) 
    """ 
    def __repr__(self):
        return "Customer(拜訪:'%s'" % (self.visiting) 
class TFacility(db.Model):
    __tablename__ = 'TFacility'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    address=db.Column(db.String(64))





    #--202302新增
    add_to_customer = db.relationship("TCustomer", backref="TFacility")


    def __init__(self, **kwargs):
        for property, value in kwargs.items():
                # depending on whether value is an iterable or not, we must
                # unpack it's value (when **kwargs is request.form, some values
                # will be a 1-element list)
                if hasattr(value, '__iter__') and not isinstance(value, str):
                    # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                    value = value[0]

                setattr(self, property, value)
        return

    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    def check_key(self,dic,key,value=None):
       
        result=None
        try:
            result=dic[key]
        except KeyError:
            result=value
        return result
    def add_new(self,dic=None):
    
        result=False
        if dic:
            id=self.check_key(  dic,"id")
        else:
            id=self.id
        if id is None:
            print("錯誤ID",dic["id"])
            return result
        
        fac=TFacility.query.filter_by(id=id).first()
        if not fac:
            if dic:
                self.id          = self.check_key(  dic,"id") 
                self.name  = self.check_key(  dic,"name")  
                self.address    = self.check_key(  dic,"address") 
                
            db.session.add(self)
            db.session.commit()
            result=True
        else:
            print("---重複產出----")
        return result
    def __repr__(self):
        return "Facility(id='%s', 名稱:'%s', 地址:'%s', 屬於客戶:'%s'" % (
                   self.id, self.name, self.address,self.add_to_customer)
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
       #return self.name
import datetime
#每一次地拜訪或是會晤都算是一個TActivity->多個TActivity組成一個TProjects
relations = db.Table('relations',
                     db.Column('visiting_id', db.Integer, db.ForeignKey('TVisiting.id')),
                     db.Column('customer_id', db.Integer, db.ForeignKey('TCustomer.id'))
                     )
class TEvent(db.Model):

#class TActivity(db.Model):

    __tablename__ = 'TVisiting'
       #return self.name
    id = db.Column(db.Integer, primary_key=True)
    #我們這邊誰發起或是負責這項活動。
    ownerid=db.Column(db.String(64))
    #這次有哪些客戶參與
    facilityid=db.Column(db.String(64))
    customerList=db.Column(db.String(255))
    starttime=db.Column(db.DateTime)
    endtime=db.Column(db.DateTime)
    nexttime=db.Column(db.DateTime)
    #甚麼樣類型的拜訪，0寫信，1.LINE(訊息)，2.十分鐘內的通話，3.30分鐘的通話，4.會面，5.面對面三人以上會議，-99。再會。
    type=db.Column(db.Integer)
    description=db.Column(db.Text)
    nextstep=db.Column(db.Text)
    #supervisor的建議。
    recommand=db.Column(db.Text)
    
    priority=db.Column(db.Integer,default=50)
    winrate=db.Column(db.Integer,default=50)
    customerType=db.Column(db.Integer,default=0)    
    
    
    
    ##--202301全部放在這搞定
    customerList = db.relationship('TCustomer', secondary=relations, lazy='subquery', 
                               backref=db.backref('visiting', lazy=True))
    
    def check_key(self,dic,key,value=None):
       
        result=None
        try:
            result=dic[key]
        except KeyError:
            result=value
        return result
    
        
    def check_value(self,value):
        
        if value is None:
            
            if value ==self.type:
                value=0
            else:
                value="None"
        elif type(value)==datetime.datetime:
            value=value.strftime("%Y/%m/%d:%H:%M:%S")
        return value
    ##--20220720 CloudMajesy的寫法。
    def add_new(self,dic=None):
    
        result=False
        id=self.check_key(  dic,"id")
        if id is None:
            print("錯誤ID",dic["id"])
            return result
            
            
            
        act=TActivity.query.filter_by(id=id).first()
        if not act:
            if dic:
                self.id             =self.check_key(dic,"id",self.id) 
                self.ownerid        =self.check_key(dic,"ownerid",self.ownerid      )
                self.facilityid     =self.check_key(dic,"facilityid",self.facilityid   )
                self.customerList   =self.check_key(dic,"customerList",self.customerList )
                self.starttime      =self.check_key(dic,"starttime",self.starttime    )
                self.endtime        =self.check_key(dic,"endtime",self.endtime      )
                self.nexttime       =self.check_key(dic,"nexttime"    ,self.nexttime     )
                self.type           =self.check_key(dic,"type"        ,self.type         )
                self.description    =self.check_key(dic,"description" ,self.description  )
                self.nextstep       =self.check_key(dic,"nextstep"    ,self.nextstep     )
                self.recommand      =self.check_key(dic,"recommand"   ,self.recommand    )
                self.priority       =self.check_key(dic,"priority"    ,self.priority     )
                self.winrate        =self.check_key(dic,"winrate"     ,self.winrate      )
                self.customerType   =self.check_key(dic,"customerType",self.customerType )
            db.session.add(self)
            db.session.commit()
            result=True
            
            new_act=TActivity.query.filter_by(id=id).first()
            
        result=True
        return result
    ##--20220720 CloudMajesy的寫法。
    def update_new(self,dic=None):
    
        result=False
        id=self.check_key(  dic,"id",self.id)
        if id is None:
            print("wrong ID",)
            return result
        self.id             =self.check_key(dic,"id",self.id) 
        self.ownerid        =self.check_key(dic,"ownerid",self.ownerid      )
        self.facilityid     =self.check_key(dic,"facilityid",self.facilityid   )
        self.customerList   =self.check_key(dic,"customerList",self.customerList )
        self.starttime      =self.check_key(dic,"starttime",self.starttime    )
        self.endtime        =self.check_key(dic,"endtime",self.endtime      )
        self.nexttime       =self.check_key(dic,"nexttime"    ,self.nexttime     )
        self.type           =self.check_key(dic,"type"        ,self.type         )
        self.description    =self.check_key(dic,"description" ,self.description  )
        self.nextstep       =self.check_key(dic,"nextstep"    ,self.nextstep     )
        self.recommand      =self.check_key(dic,"recommand"   ,self.recommand    )
        self.priority       =self.check_key(dic,"priority"    ,self.priority     )
        self.winrate        =self.check_key(dic,"winrate"     ,self.winrate      )
        self.customerType   =self.check_key(dic,"customerType",self.customerType )
        db.session.flush()
        db.session.commit()
        result=True
        return result
    
    
    def update(self):
        try:
            db.session.flush()
            db.session.commit()
            print("activity updated")
        except:
            print("--error--")
        
    def commit_update(self):
        try:
            db.session.flush()
            db.session.commit()
        except:
            print("--error--")
    def __init__(self, **kwargs):
        self.customerList=""
        return
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])    
        

    def get_dic(self):
        dic={}
        dic["id"]=self.check_value(self.id   )
        dic["ownerid"]=self.check_value(self.ownerid       )
        dic["facilityid"]=self.check_value(self.facilityid   )
        
        dic["customerList"]=self.check_value(self.customerList)
        dic["endtime"]=self.check_value(self.endtime)
        dic["nexttime"]=self.check_value(self.nexttime)
        dic["starttime"]=self.check_value(self.starttime    )
        
        dic["type"]=self.check_value(self.type)
        dic["description"]=self.check_value(self.description)
        dic["nextstep"]=self.check_value(self.nextstep)
        dic["recommand"]=self.check_value(self.recommand)
        dic["priority"]=50
        dic["winrate"]=50
        dic["customerType"]=50
        return dic
    def __repr__(self):
        
        return "<TActivity(id='%s',醫院公司:'%s' 顧客們='%s', 起始時間='%s',結束時間:'%s',description='%s',Customer='%s')>" % (
                   self.id,self.facilityid, self.customerList, self.starttime,self.endtime,self.description,self.customer)
    """
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    """
        
class TDevice(db.Model):
    __tablename__ = 'TDevice'
    id = db.Column(db.Integer, primary_key=True)
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
#由多個TActivity所組成。
class TProject(db.Model):
    __tablename__ = 'TProject'
    id = db.Column(db.Integer, primary_key=True)
    #我們這邊誰發起或是負責這項活動。
    personList=db.Column(db.String(64))
    #專案或是計畫名稱
    name=db.Column(db.String(64))
    #專案類型(0代表購案，1代表投資，2代表研究合作等，3.代表跨界合作
    type=db.Column(db.Integer)
    #先前所有的活動，活動內已經有對方客戶的名稱了所以不用特別寫。
    activityList=db.Column(db.String(4069))
    #哪一個機構
    facilityid=db.Column(db.String(64))
    
    #此次活動延續自何者?之前的活動，可以視為子TProject, 過去紀錄的查詢。
    parentid=db.Column(db.Integer)
    
    
    startTime=db.Column(db.DateTime)
    endTime=db.Column(db.DateTime)
    budge=db.Column(db.Integer)
    winrate=db.Column(db.Integer)
    priority=db.Column(db.Integer)
    
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    userid = request.form.get('userid')
    user = Users.query.filter_by(userid=userid).first()
    return user if user else None
