# -*- encoding: utf-8 -*-


from flask_login import UserMixin

from apps import db, login_manager
from sqlalchemy.orm import backref
from apps.authentication.util import hash_pass
import datetime

#---關聯資料庫多對多的定義---
relationEventCustomer = db.Table('relationEventCustomer',
                     db.Column('event_id', db.Integer, db.ForeignKey('TEvent.uid')),
                     db.Column('customer_id', db.Integer, db.ForeignKey('TManager.uid'))
                     )
                     
                     
relationProjectManager = db.Table('relationProjectManager',
                     db.Column('project_id', db.Integer, db.ForeignKey('TProject.uid')),
                     db.Column('manager_id', db.Integer, db.ForeignKey('TManager.uid'))
                     )
relationProjectCustomer = db.Table('relationProjectCustomer',
                     db.Column('project_id', db.Integer, db.ForeignKey('TProject.uid')),
                     db.Column('customer_id', db.Integer, db.ForeignKey('TManager.uid'))
                     )


relationManagerUser= db.Table('relationManagerUser',
                     db.Column('manager_id', db.Integer, db.ForeignKey('TManager.uid')),
                     db.Column('user_id', db.Integer, db.ForeignKey('TUser.uid'))
                     )
relationManagerFacility= db.Table('relationManagerFacility',
                     db.Column('manager_id', db.Integer, db.ForeignKey('TManager.uid')),
                     db.Column('facility_id', db.Integer, db.ForeignKey('TFacility.uid'))
                     )


class TPeople(db.Model):
    __abstract__ = True
    
    uid             =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    gender          =db.Column(db.Integer)
    height          =db.Column(db.Integer)
    weight          =db.Column(db.Integer)
    registerTime    =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    accountId       =db.Column(db.String(64),unique=False)
    realName        =db.Column(db.String(64),unique=False)
    password        =db.Column(db.LargeBinary)
    localPhone      =db.Column(db.String(64),unique=False)
    cellPhone       =db.Column(db.String(64),unique=False)
    eMail           =db.Column(db.String(64),unique=False)
    messengerId     =db.Column(db.String(64),unique=False)
    jobTitle        =db.Column(db.String(64),unique=False)
    uploadStatus    =db.Column(db.Integer,unique=False)
    birthday        =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    nationalId      =db.Column(db.String(64),unique=False)
    loginDate       =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    portraitCode    =db.Column(db.String(64),unique=False)
    ip              =db.Column(db.String(64),unique=False)
    #bossID     =db.Column(db.Integer, db.ForeignKey('TPeople.uid'))
    #underlingLIST   =db.relationship('TPeople', remote_side=[bossID])
    
    """
    activityList    =db.relationship("TActivity", backref="TPeople")
    eventLIST       =db.relationship("TEvent", backref="TPeople")
    facilityLIST    =db.relationship('TFacility', secondary=relationPeopleFacility, lazy='subquery', backref=db.backref('peopleLIST', lazy=True))
    """
    #projectLIST
    #deviceLIST
    """
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    """
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   
class TManager(TPeople):
    __tablename__ = 'TManager'
    level           =db.Column(db.Integer)
    bossID          =db.Column(db.Integer, db.ForeignKey('TManager.uid'))
    
    #------一對多的多方----------------
    #customersFacilityID=db.Column(db.Integer, db.ForeignKey('TFacility.uid'))
    #------一對多的一方----------------
    
    activityLIST    =db.relationship("TActivity", backref="TManager")
    eventLIST       =db.relationship("TEvent", backref="TManager")
    submanagerLIST  =db.relationship('TManager', remote_side=[bossID])   
    
    invitationLIST  =db.relationship("TInvitation", backref="TManager")    
    #------多對多的啟動方----------------    
    userLIST        =db.relationship('TUser', secondary=relationManagerUser, lazy='subquery', backref=db.backref('managerLIST', lazy=True))
    facilityLIST    =db.relationship('TFacility', secondary=relationManagerFacility, lazy='subquery', backref=db.backref('managerLIST', lazy=True))
    prescriptionLIST=db.relationship("TPrescription", backref="TManager")
    #projectLIST
    #deviceLIST
    def __init__(self):
        return
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    def __repr__(self):
        
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   
    
class TUser(TPeople):
    __tablename__ = 'TUser'
    activityHistrorySummary    =db.Column(db.String(512),unique=False)
    doctorAdvise               =db.Column(db.String(512),unique=False)
    disease                    =db.Column(db.Integer,unique=False)
    chartNumber                =db.Column(db.String(64),unique=False)
    trainingMode               =db.Column(db.Integer,unique=False)

    #=====RB
    shopPoints                  =db.Column(db.Integer,unique=False)
    activationStatus            =db.Column(db.Integer,unique=False)
    redeemedCoupons             =db.Column(db.String(64),unique=False)
    managerPairingCode          =db.Column(db.String(64),unique=False)
    
    #------一對多的一方----------------    
    prescriptionLIST    =db.relationship("TPrescription", backref="TUser")
    activityLIST        =db.relationship("TActivity", backref="TUser")
    invitationLIST      =db.relationship("TInvitation", backref="TUser")
    #------一對多的多方----------------        
    facilityID = db.Column(db.Integer, db.ForeignKey('TFacility.uid'))
    #------一對一的啟動方----------------        
    deviceID = db.Column(db.Integer, db.ForeignKey('TDevice.uid'))
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   
    
class TFacility(db.Model):
    __tablename__ = 'TFacility'
    uid             =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    key                 =db.Column(db.String(128),unique=False)
    uploadStatus        =db.Column(db.Integer,unique=False)
    city                =db.Column(db.String(64),unique=False)
    pruduct             =db.Column(db.String(32),unique=False)
    displayName         =db.Column(db.String(128),unique=False)
    registerTime        =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    phone               =db.Column(db.String(32),unique=False)
    address             =db.Column(db.String(256),unique=False)
    email               =db.Column(db.String(64),unique=False)
    group               =db.Column(db.String(64),unique=False)
    vender              =db.Column(db.String(64),unique=False)
    latitude            =db.Column(db.Float,unique=False)
    longitude           =db.Column(db.Float,unique=False)
    bossID              =db.Column(db.Integer, db.ForeignKey('TFacility.uid'))
    
    #------自身一對多的一方----------------    
    subfacilityLIST      =db.relationship('TFacility', remote_side=[bossID])
    #------一對多的一方---------------
    activityList        =db.relationship("TActivity", backref="TFacility")
    userList            =db.relationship("TUser", backref="TFacility")
    #customerList        =db.relationship("TManager", backref="TFacility")#在TFacility內, 對應TManager內的customersFacilityID
    deviceList          =db.relationship("TDevice", backref="TFacility")#在TFacility內, 對應TDevice內的facilityID
    eventList           =db.relationship("TEvent", backref="TFacility")#在TFacility內
    
    
    
    """
    customerList=db.relationship("TCustomer", backref="TFacility")#在TFacility內, 一對多的一
    deviceList=db.relationship("TDevice", backref="TFacility")#在TFacility內一對多的一
    eventList=db.relationship("TEvent", backref="TFacility")#在TFacility內一對多的一
    """
    def __init__(self):
        return
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    def __repr__(self):
        return "Facility(id='%s', 名稱:'%s', 地址:'%s', 屬於客戶:'%s',活動次數:'%s'\n" % (
                   self.id, self.name, self.address,self.customerList,self.eventList)
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
       
    """
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
    """
class TActivity(db.Model):
    __tablename__   = 'TActivity'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    key                 =db.Column(db.String(128),unique=False)
    calories            =db.Column(db.Float,unique=False)
    note                =db.Column(db.String(512),unique=False)
    finishRate          =db.Column(db.Integer,unique=False)
    startTime           =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    productType         =db.Column(db.Integer,unique=False)
    dispName            =db.Column(db.String(128),unique=False)
    jointId             =db.Column(db.Integer,unique=False)
    uploadStatus        =db.Column(db.Integer,unique=False)
    duration            =db.Column(db.Integer,unique=False)
    score               =db.Column(db.Float,unique=False)
    
    #-----一對多的多方---------------
    deviceID            = db.Column(db.Integer, db.ForeignKey('TDevice.uid'))
    managerID           = db.Column(db.Integer, db.ForeignKey('TManager.uid'))
    facilityID          = db.Column(db.Integer, db.ForeignKey('TFacility.uid'))
    userID              = db.Column(db.Integer, db.ForeignKey('TUser.uid'))
    def __init__(self):
        return
    def __repr__(self):
        
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class TDevice(db.Model):
    __tablename__   = 'TDevice'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    mac                 =db.Column(db.String(64),unique=False)
    deviceName          =db.Column(db.String(64),unique=False)
    product             =db.Column(db.String(32),unique=False)
    cpu                 =db.Column(db.String(64),unique=False)
    ram                 =db.Column(db.Integer,unique=False)
    gpu                 =db.Column(db.String(64),unique=False)
    os                  =db.Column(db.String(64),unique=False)
    deviceMode          =db.Column(db.String(64),unique=False)
    #-----一對多的多方---------------
    facilityID          =db.Column(db.Integer, db.ForeignKey('TFacility.uid'))
    #facilityLIST
    #managerLIST
    #-----一對一的接受方----
    userLINK = db.relationship('TUser', backref=db.backref('TUser', uselist=False))
    
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class TPrescription(db.Model):
    __tablename__   = 'TPrescription'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    key                 =db.Column(db.String(64),unique=False)
    days                =db.Column(db.Integer,unique=False)
    introduction        =db.Column(db.String(256),unique=False)
    displayName         =db.Column(db.String(128),unique=False)
    pictureCode         =db.Column(db.String(64),unique=False)
    prices              =db.Column(db.Integer,unique=False)
    shopTags            =db.Column(db.String(256),unique=False)
    releaseDate         =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    target              =db.Column(db.Integer,unique=False)
    #------一對多的一方----------------    
    settingLIST=db.relationship("TSetting", backref="TPresecription")
    #------一對多的多方---------------
    managerID = db.Column(db.Integer, db.ForeignKey('TManager.uid'))    
    userID = db.Column(db.Integer, db.ForeignKey('TUser.uid'))    
    
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class TContent(db.Model):
    __tablename__   = 'TContent'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    key                 =db.Column(db.String(64),unique=False)
    #title               =db.Column(db.String(512),unique=False)
    iconImage           =db.Column(db.String(64),unique=False)
    targetAction        =db.Column(db.Integer,unique=False)
    #category            =db.Column(db.String(64),unique=False)
    author              =db.Column(db.String(64),unique=False)#db.Column(db.Integer, db.ForeignKey('TManager.uid'))  
    company             =db.Column(db.String(64),unique=False)#db.Column(db.Integer, db.ForeignKey('TFacility.uid'))  
    story               =db.Column(db.String(256),unique=False)
    
    #------一對多的一方---------------
    settingLIST        =db.relationship('TSetting', backref='TContent')
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class TSetting(db.Model):
    __tablename__   = 'TSetting'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    trainingLifeTime    =db.Column(db.Integer,unique=False)
    difficulty          =db.Column(db.Integer,unique=False)
    targetScore         =db.Column(db.Integer,unique=False)
    targetJoints        =db.Column(db.Integer,unique=False)
    cameraMode          =db.Column(db.Integer,unique=False)
    maxUser             =db.Column(db.Integer,unique=False)
    trainingDateIndex   =db.Column(db.Integer,unique=False)
    exeDate             =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    
    #------一對多的多方---------------
    contentID           = db.Column(db.Integer, db.ForeignKey('TContent.uid')) 
    prescriptionID      = db.Column(db.Integer, db.ForeignKey('TPrescription.uid'))
    
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class TInvitation(db.Model):
    __tablename__   = 'TInvitation'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    code                =db.Column(db.String(64),unique=False)
    inviteAction        =db.Column(db.Integer,unique=False)
    createDate          =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    expireDate          =db.Column(db.DateTime(timezone=True),unique=False,default=datetime.datetime.utcnow()+datetime.timedelta(hours=8))
    message             =db.Column(db.String(512),unique=False)
    #---------一對多的一-------------------
    #managerLIST         =db.relationship("TManager", backref="TInvitation")
    #managerLIST         =db.relationship("TManager", backref="TInvitation")
    #---------一對多的多-------------------
    senderID            =db.Column(db.Integer, db.ForeignKey('TManager.uid'))
    userID              =db.Column(db.Integer, db.ForeignKey('TUser.uid'))
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class TEvent(db.Model):
    __tablename__   = 'TEvent'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    
    startTime=db.Column(db.DateTime(timezone=True),unique=False)
    endTime=db.Column(db.DateTime(timezone=True),unique=False)
    nextTime=db.Column(db.DateTime(timezone=True),unique=False)
    #甚麼樣類型的拜訪，0寫信，1.LINE(訊息)，2.十分鐘內的通話，3.30分鐘的通話，4.會面，5.面對面三人以上會議，-99。再會。
    type=db.Column(db.Integer)
    description=db.Column(db.Text)
    nextStep=db.Column(db.Text)
    #supervisor的建議。
    recommand=db.Column(db.Text)
    
    priority=db.Column(db.Integer,default=50)
    winrate=db.Column(db.Integer,default=50)
    customerType=db.Column(db.Integer,default=0)    

    ##--202301全部放在這搞定
    
    #--------多對多的發動方-------------------    
    customerID      =db.relationship('TManager', secondary=relationEventCustomer, lazy='subquery', backref=db.backref('customereventLIST', lazy=True))
    
    #--------一對多的多-------------------    
    
    managerID       =db.Column(db.Integer, db.ForeignKey('TManager.uid'))#TEvent內一對多的多
    facilityID      =db.Column(db.Integer, db.ForeignKey('TFacility.uid'))#TEvent內一對多的多
    projectID       =db.Column(db.Integer, db.ForeignKey('TProject.uid'))#TEvent內一對多的多
    
    
    
    
    
    
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   
class TProject(db.Model):
    __tablename__   = 'TProject'
    uid                 =db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)

    #專案或是計畫名稱
    displayName=db.Column(db.String(64))
    #專案類型(0代表購案，1代表投資，2代表研究合作等，3.代表跨界合作
    type=db.Column(db.Integer)
    #先前所有的活動，活動內已經有對方客戶的名稱了所以不用特別寫。
    #activityList=db.Column(db.String(4069))
    #哪一個機構
    #facilityid=db.Column(db.String(64))
    
    #此次活動延續自何者?之前的活動，可以視為子TProject, 過去紀錄的查詢。
    parentid=db.Column(db.Integer)
    
    
    startTime=db.Column(db.DateTime)
    endTime=db.Column(db.DateTime)
    budge=db.Column(db.Integer)
    winrate=db.Column(db.Integer)
    priority=db.Column(db.Integer)
    
    #--202302新增----
    #--------一對多的一-------------------
    eventList       =db.relationship("TEvent", backref="TProject")#在TProject內
    #--------多對多的發起方
    managerList     =db.relationship('TManager', secondary=relationProjectManager, lazy='subquery', backref=db.backref('projectLIST', lazy=True))
    customerList    =db.relationship('TManager', secondary=relationProjectCustomer, lazy='subquery', backref=db.backref('customerprojectLIST', lazy=True))
    
    
    def __init__(self):
        return
    def __repr__(self):
        return
    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   
    



    

    
@login_manager.user_loader
def user_loader(id):
    return TManager.query.filter_by(uid=id).first()

@login_manager.request_loader
def request_loader(request):
    userid = request.form.get('userid')
    user = TManager.query.filter_by(accountId=userid).first()
    return user if user else None
