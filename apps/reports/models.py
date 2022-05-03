from collections import OrderedDict
isFlask=True
if isFlask:    
    from apps import db
    from apps.authentication.util import hash_pass
    Base=db.Model
    
else:
    import time
    import json
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from sqlalchemy import Column, String, Integer, Float, VARCHAR
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    db_path = "sqlite:///longgoodDB.bytes"
    engine = create_engine(db_path) 
#from sqlalchemy.ext.declarative import declarative_base
class TManager(Base):
    __tablename__ = 'TManager'
    if isFlask:
        id          = db.Column(db.Integer, primary_key=True)
        managerid   = db.Column(db.String(64), unique=True)
        name        = db.Column(db.String(64), unique=False)
        email       = db.Column(db.String(64), unique=True)
        password    = db.Column(db.LargeBinary)
        facilityid  =db.Column(db.String(64),unique=False)
        phone       =db.Column(db.String(64),unique=False)
        submanager  =db.Column(db.String(64),unique=False)
        patients    =db.Column(db.String(64),unique=False)
        gender      =db.Column(db.String(64),unique=False)
        picture     =db.Column(db.String(64),unique=False)
        ip          =db.Column(db.String(64),unique=False)
        logintime   =db.Column(db.String(64),unique=False)
    else:
        id          = Column(Integer, primary_key=True)
        managerid   = Column(String(64), unique=True)
        name        = Column(String(64), unique=False)
        email       = Column(String(64), unique=True)
        password    = Column(LargeBinary)
        facilityid  =Column(String(64),unique=False)
        phone       =Column(String(64),unique=False)
        submanager  =Column(String(64),unique=False)
        patients    =Column(String(64),unique=False)
        gender      =Column(String(64),unique=False)
        picture     =Column(String(64),unique=False)
        ip          =Column(String(64),unique=False)
        logintime   =Column(String(64),unique=False)
        
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

    def __repr__(self):
        return str(self.name)


class TUserInfo(Base):
    __tablename__="TUserInfo"
    
    if isFlask:
        userid      =   db.Column(db.VARCHAR(140), primary_key=True)
        realname    =   db.Column(db.VARCHAR(140))
        nationalid  =   db.Column(db.VARCHAR(140))
        birthday    =   db.Column(db.VARCHAR(140))
        disease     =   db.Column(db.VARCHAR(140))
        height      =   db.Column(db.Integer)
        weight      =   db.Column(db.Integer)
        gender      =   db.Column(db.VARCHAR(140))
        phone       =   db.Column(db.VARCHAR(140))
        facilityid  =   db.Column(db.VARCHAR(140))
        status      =   db.Column(db.Integer)
        deviceid    =   db.Column(db.VARCHAR(140))
        note        =   db.Column(db.VARCHAR(140))
        therapist   =   db.Column(db.VARCHAR(140))
        patientid   =   db.Column(db.VARCHAR(140))
        trainingmode=   db.Column(db.VARCHAR(140))
        duration    =   db.Column(db.VARCHAR(140))
        registertime=   db.Column(db.VARCHAR(140))
    else:
        userid      =   Column(VARCHAR(140), primary_key=True)
        realname    =   Column(VARCHAR(140))
        nationalid  =   Column(VARCHAR(140))
        birthday    =   Column(VARCHAR(140))
        disease     =   Column(VARCHAR(140))
        height      =   Column(Integer)
        weight      =   Column(Integer)
        gender      =   Column(VARCHAR(140))
        phone       =   Column(VARCHAR(140))
        facilityid  =   Column(VARCHAR(140))
        status      =   Column(Integer)
        deviceid    =   Column(VARCHAR(140))
        note        =   Column(VARCHAR(140))
        therapist   =   Column(VARCHAR(140))
        patientid   =   Column(VARCHAR(140))
        trainingmode=   Column(VARCHAR(140))
        duration    =   Column(VARCHAR(140))
        registertime=   Column(VARCHAR(140))
    
    def set_phone(self):
        if self.phone is None or self.phone=="":
            self.phone="尚未輸入"
        return
    def set_therapist(self):
        if self.therapist is None or self.therapist=="":
            self.therapist="尚未指派"
           
        return

    def set_age(self):
            birthstring=self.birthday
            result=""
            try:
                birth=time.strptime(birthstring,"%Y/%m/%d")
                today = time.localtime( time.time())
                
                year=today.tm_year-birth.tm_year
                month=today.tm_mon-birth.tm_mon
                days=today.tm_mday-birth.tm_mday
                delta_year=0
                if month>0:
                    delta_year=1
                result=year-1+delta_year
            except ValueError:
                print("[ValueError]")
            self.birthday=result
    def set_gender(self):
                value=self.gender

                if value=="Femal" or "Female":
                    value="女性"
                elif value=="Male" or "Mal":
                    value="男性"
                self.gender=value
    def check_key(self,dic,key):
        print("check_key:",key)
        result=None
        try:
            result=dic[key]
            if result == "NULLUSER":
                result=None
        except KeyError:
            result=None
        return result
    def get_dic(self):
        patientInfos={}
        patientInfos["userid"]=self.userid
        patientInfos["realname"]=self.realname
        patientInfos["nationalid"]=self.nationalid
        patientInfos["birthday"]=self.birthday
        patientInfos["disease"]=self.disease
        patientInfos["height"]=self.height
        patientInfos["weight"]=self.weight
        patientInfos["gender"]=self.gender
        patientInfos["phone"]=self.phone
        patientInfos["facilityid"]=self.facilityid
        patientInfos["status"]=self.status
        patientInfos["deviceid"]=self.deviceid
        patientInfos["note"]=self.note
        patientInfos["therapist"]=self.therapist
        patientInfos["patientid"]=self.patientid
        patientInfos["trainingmode"]=self.trainingmode
        patientInfos["duration"]=self.duration
        patientInfos["registertime"]=self.registertime
        return patientInfos
    def add_new(self,dic):
        if self.check_key(  dic,"userid") is None:
            print("錯誤ID",dic["userid"])
            return False
        self.userid      = self.check_key(  dic,"userid")  
        self.realname    = self.check_key(  dic,"realname")  
        self.nationalid  = self.check_key(  dic,"nationalid")  
        self.birthday    = self.check_key(  dic,"birthday") 
        self.disease     = self.check_key(  dic,"disease") 
        self.height      = self.check_key(  dic,"height") 
        self.weight      = self.check_key(  dic,"weight")  
        self.gender      = self.check_key(  dic,"gender")  
        self.phone       = self.check_key(  dic,"phone") 
        self.facilityid  = self.check_key(  dic,"facilityid")  
        self.status      = self.check_key(  dic,"status")  
        self.deviceid    = self.check_key(  dic,"deviceid")  
        self.note        = self.check_key(  dic,"note")  
        self.therapist   = self.check_key(  dic,"therapist")
        
        
        self.patientid   = self.check_key(  dic,"patientid")
        self.trainingmode= self.check_key(  dic,"trainingmode")
        self.duration    = self.check_key(  dic,"duration")
        self.registertime= self.check_key(  dic,"registertime")
        return True
    
    def __repr__(self):
        return "使用者(id='%s', name='%s', 性別='%s',nationalid='%s',deviceid:'%s',facilityid:'%s')" % (
                   self.userid, self.realname, self.gender,self.nationalid,self.deviceid,self.facilityid)

class TFacility(Base):
    __tablename__="TFacility"
    if isFlask:
        facilityid      = db.Column(db.VARCHAR(140), primary_key=True)
        name            = db.Column(db.VARCHAR(140))
        deviceids       = db.Column(db.VARCHAR(140))
        phone           = db.Column(db.VARCHAR(140))
        address         = db.Column(db.VARCHAR(140))
        email           = db.Column(db.VARCHAR(140))
        group           = db.Column(db.VARCHAR(140))
        vender          = db.Column(db.VARCHAR(140))
        registertime    = db.Column(db.VARCHAR(140))
    else:
        facilityid      = Column(VARCHAR(140), primary_key=True)
        name            = Column(VARCHAR(140))
        deviceids       = Column(VARCHAR(140))
        phone           = Column(VARCHAR(140))
        address         = Column(VARCHAR(140))
        email           = Column(VARCHAR(140))
        group           = Column(VARCHAR(140))
        vender          = Column(VARCHAR(140))
        registertime    = Column(VARCHAR(140))
        
    def check_key(self,dic,key):
        print("key:",key)
        result=None
        try:
            result=dic[key]
            if result == "NULLACTIVITY":
                result=None
        except KeyError:
            result=None
        return result
    def add_new(self,dic):
        if self.check_key(  dic,"facilityid") is None:
            print("錯誤ID",dic["facilityid"])
            return False
        self.facilityid      = self.check_key(  dic,"facilityid")   
        self.name            = self.check_key(  dic,"name")   
        self.deviceids       = self.check_key(  dic,"deviceids")   
        self.phone           = self.check_key(  dic,"phone")   
        self.address         = self.check_key(  dic,"address")   
        self.email           = self.check_key(  dic,"email")   
        self.group           = self.check_key(  dic,"group")   
        self.vender          = self.check_key(  dic,"vender")   
        self.registertime    = self.check_key(  dic,"registertime")  
        return True
    def __repr__(self):
        return "<TFacility(id='%s', name='%s', address='%s',管理機器:'%s',註冊時間:'%s')>" % (
                   self.facilityid, self.name, self.address,self.deviceids,self.registertime)

class TActRaw(Base):
    __tablename__ = 'TActRaw'
    
    if isFlask:
        activityid  = db.Column(db.VARCHAR(140), primary_key=True)
        scorejson   = db.Column(db.VARCHAR(140))
        timejson    = db.Column(db.VARCHAR(140))
        jointjson   = db.Column(db.VARCHAR(140))
        jointposjson= db.Column(db.VARCHAR(140))
    else:
        activityid  = Column(VARCHAR(140), primary_key=True)
        scorejson   = Column(VARCHAR(140))
        timejson    = Column(VARCHAR(140))
        jointjson   = Column(VARCHAR(140))
        jointposjson= Column(VARCHAR(140))
    
    def __repr__(self):
        return "<TActRaw(name='%s', fullname='%s', password='%s')>" % (
                   self.activityid, self.scorejson, self.timejson)

class TActivity(Base):
    # 指定本类映射到users表
    __tablename__ = 'TActivity'
    if isFlask:
    # 指定name映射到name字段; name字段为字符串类形，
        activityid      = db.Column(db.VARCHAR(140), primary_key=True)
        userid          = db.Column(db.VARCHAR(140))
        facilityid      = db.Column(db.VARCHAR(140))
        activityname    = db.Column(db.VARCHAR(140))
        starttime       = db.Column(db.VARCHAR(140))
        duration        = db.Column(db.Float)
        score           =db.Column(db.Float)
        scoreACT        =db.Column(db.Float)
        status          =db.Column(db.Integer)
        jointid         = db.Column(db.Integer)
        
    else:
        activityid  = Column(VARCHAR(140), primary_key=True)
        userid      = Column(VARCHAR(140))
        facilityid  = Column(VARCHAR(140))
        activityname= Column(VARCHAR(140))
        starttime   = Column(VARCHAR(140))
        duration    = Column(Float)
        score       = Column(Float)
        scoreACT    = Column(Float)
        status      = Column(Integer)
        jointid     = Column(Integer)
    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def check_key(self,dic,key):
        result=None
        try:
            result=dic[key]
            if result == "None":
                result=None
                
        except KeyError:
            result=None

        return result
    def add_new(self,dic):
        if self.check_key(dic,"activityid") is None:
            print("錯誤ID",dic["activityid"])
            return False
        self.activityid  = self.check_key(  dic,"activityid") 
        self.userid      = self.check_key(  dic,"userid")  
        self.facilityid  = self.check_key(  dic,"facilityid")  
        self.activityname= self.check_key(  dic,"activityname") 
        self.starttime   = self.check_key(  dic,"starttime") 
        self.duration    = self.check_key(  dic,"duration") 
        self.score       = self.check_key(  dic,"score")  
        self.scoreACT    = self.check_key(  dic,"scoreACT")  
        self.status      = self.check_key(  dic,"status")  
        self.jointid     = self.check_key( dic,"jointid")  
        
        return True
    def __repr__(self):
        return "<TActivity(starttime='%s', activityname='%s',actid='%s',userid='%s')>" % (
                   self.starttime, self.activityname,self.activityid,self.userid)
import time
class RDatabase():#比較接近c sharp內的namespace
    name="外層"
    class RDatabase():
        name="核心，我是名字"
        def __init__(self):
            self.name="核心，真!!"
            return
        def __init__(self):
            if isFlask:
                self.session=db.session
            else:
                self.name="核心，真!!"
                Session = sessionmaker()
                Session.configure(bind=engine)
                self.session = Session() #然后就可以使用session进行查询操作了
            return
        #輸入日期與病人id，來取得活動細節。
        def get_activities(self,userid,dateList):
            new_raws=[]
            raws=TActivity.query.filter_by(userid=userid)
            new_raws=[]
            for act in raws:
                detail_date=act.starttime
                f_date = time.strptime(detail_date.split('T')[0], "%Y-%m-%d")
                datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
                for date in dateList:
                    if datestring==date:
                        new_raws.append(act)
            return new_raws
        def get_last_day(self,userid):
            #datestring="2022-03-22"
            data=TActivity.query.filter_by(userid=userid).order_by(TActivity.starttime.desc()).first()
            result=data.starttime.split('T')
            f_date = time.strptime(result[0], "%Y-%m-%d")
            datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
            print("----get last day--------------")
            return [datestring,""]
        def get_12days(self,userid):

            rows=TActivity.query.filter_by(userid=userid).order_by(TActivity.starttime.desc())
            dateList=[]
            for act in rows:
                date=act.starttime
                result=date.split('T')
                f_date = time.strptime(date.split('T')[0], "%Y-%m-%d")
                datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
                dateList.append(datestring)
            singledateList=list(OrderedDict.fromkeys(dateList))
            length=len(singledateList)
            if length>12:
                length=12
            result=[]
            for i in range(length):
                result.append(singledateList[i])
            days=sorted(result)
            print("---------get 12天------------")
            return days 
            
        def add_new_user(self,user):
            count=0
            
            tmpuser=TUserInfo(
                )
            result=tmpuser.add_new(user)
            if result is True:
                if self.check_user(tmpuser.userid) ==False: #代表不存在
                    self.session.add(tmpuser)
                    count=count+1
                    print("**新增",tmpuser)
                else:
                    print("新增使用者錯誤002")
            else:
                print("新增使用者錯誤001")
            self.session.commit()
            print("此次新增User:",count)
        def add_new_activity(self,act):
            count=0

            tmpact=TActivity(
                )
            result=tmpact.add_new(act)
            if result is True:
                if self.check_activity(tmpact.activityid) ==False: #代表不存在
                    self.session.add(tmpact)
                    count=count+1
               
            self.session.commit()
            print("此次新增TActivity:",count)
        def add_new_actraw(self,act):
            count=0
            
            tmpact=TActRaw(
                )
            result=tmpact.add_new(act)
            if result is True:
                if self.check_actraw(tmpact.activityid) ==False: #代表不存在
                    self.session.add(tmpact)
                    count=count+1
            self.session.commit()
            print("此次新增:",count)
        def add_new_facility(self,fac):
            count=0
            
            tmpfac=TFacility(
                )
            result=tmpfac.add_new(fac)
            if result is True:
                if self.check_facility(tmpfac.facilityid) ==False: #代表不存在
                    self.session.add(tmpfac)
                    count=count+1
            self.session.commit()
            print("此次新增Facility:",count)
        def check_user(self,userid):
            user=self.session.query(TUserInfo).filter_by(userid=userid).first()
            if user is not None:
                return True
            else:
                return False
        def check_activity(self,activityid):
            act=self.session.query(TActivity).filter_by(activityid=activityid).first()
            if act is not None:
                return True
            else:
                return False
        def check_actraw(self,activityid):
            act=self.session.query(TActRaw).filter_by(activityid=activityid).first()
            if act is not None:
                return True
            else:
                return False
        def check_facility(self,facilityid):
            facility=self.session.query(TFacility).filter_by(facilityid=facilityid).first()
            if facility is not None:
                return True
            else:
                return False
#----------------------------------------------------------------------

 
        def get_user(self,userid,case=1):
            
            if case==1:
                user=self.session.query(TUserInfo).filter_by(userid=userid).first()
            elif case==2:
                user=self.session.query(TUserInfo).filter_by(nationalid=userid).first()
            elif case==3:
                user=self.session.query(TUserInfo).filter_by(nationalid=userid).first()
            elif case==4:
                user=self.session.query(TUserInfo).filter_by(realname=userid).first()
            
            if user is None:
                print("User is None:")
                return TUserInfo(),None
            
            last_day=self.get_last_day(userid);
            user.set_age()
            user.set_gender()
            user.set_phone()
            user.set_therapist()
            
            dic=user.get_dic()
            dic["registertime"]=last_day[0]
            return user,dic
        def get_userlist(self):
            user=[]
            user=self.session.query(TUserInfo).order_by(TUserInfo.userid)
            return user    
        def get_activitylist(self):
            result=[]
            result=self.session.query(TActivity)
            return result    
        def get_actrawlist(self):
            result=[]
            result=self.session.query(TActRaw)
            return result    
        def get_facilitylist(self):
            result=[]
            result=self.session.query(TFacility)
            return result    
        def get_facility(self,facilityid):
            
            result=self.session.query(TFacility).filter_by(facilityid=facilityid).first()
            return result    
        
        def get_actraw(self,activityid):
            raws=[]
            if isFlask:
                raws=TActRaw.query.filter_by(activityid=activityid).first()
            else:
                raws=self.session.query(TActRaw).filter_by(activityid=activityid).first()
            return raws
            
        def get_user_deviceid(self,deviceid):
            user=self.session.query(TUserInfo).filter_by(deviceid).first()
            return user
        #根據輸入的case,來決定value作為query值要看那些東西。
        def get_activity(self,value,case):
            if case==1:#activityid
                raws=self.session.query(TActivity).filter_by(activityid=value).order_by(TActivity.starttime.asc()).first()
            elif case==2:#userid
                raws=self.session.query(TActivity).filter_by(userid=value).order_by(TActivity.starttime.asc()).first()
            elif case==3:#deviceid
                raws=self.session.query(TActivity).filter_by(deviceid=value).order_by(TActivity.starttime.asc()).first()
            
            return raws
        #輸入日期與病人id，來取得活動細節。
        def get_activities(self,userid=None,dateList=None):
            new_raws=[]
            if userid is None:
                raws=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc())
            else:
                raws=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc())
            new_raws=[]
            if dateList is None:
                return raws
            for act in raws:
                detail_date=act.starttime

                if detail_date is not None:
                    f_date = time.strptime(detail_date.split('T')[0], "%Y-%m-%d")
                    datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
                    for date in dateList:
                        if datestring==date:
                            new_raws.append(act)
            return new_raws
        def get_activity_actname(self,userid=None,activityname=None):
            new_raws=[]
            if userid is None and activityname is None:
                print("都沒有，回傳全部")
                raws=self.session.query(TActivity).order_by(TActivity.starttime.asc())
            
            elif userid is None:
                print("只有actname",activityname)
                raws=self.session.query(TActivity).filter_by(activityname=activityname).order_by(TActivity.starttime.asc())
            elif activityname is None:
                print("只有使用者名稱",userid)
                raws=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc())
            else:
                raws=self.session.query(TActivity).filter_by(userid=userid,activityname=activityname).order_by(TActivity.starttime.asc())
                
            return raws
            
             
        def get_last_day(self,userid):
            data=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc()).first()
            if data is None or data.starttime is None:
                return ["None",""]
                
            print("----starttime:",data.starttime)
            result=data.starttime.split('T')
            f_date = time.strptime(result[0], "%Y-%m-%d")
            datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
            return [datestring,""]
        def get_12days(self,userid,activityname=None):
            from collections import OrderedDict
            if activityname is None:
                rows=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc())
            else:
                rows=self.session.query(TActivity).filter_by(userid=userid,activityname=activityname).order_by(TActivity.starttime.asc())
            dateList=[]
            actidList=[]
            for act in rows:
                date=act.starttime
                result=date.split('T')
                f_date = time.strptime(date.split('T')[0], "%Y-%m-%d")
                datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
                dateList.append(datestring)
                actidList.append(act.activityid)
            singledateList=list(OrderedDict.fromkeys(dateList))
            length=len(singledateList)
            startIndex=0
            if length>=12:
                startIndex=length-12
            result=[]
            for i in range(startIndex,length):
                result.append(singledateList[i])
            days=sorted(result)
            
            return days 
        def get_12times(self,userid,activityname=None):
            if activityname is None:
                rows=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc())
                count=self.session.query(TActivity).filter_by(userid=userid).order_by(TActivity.starttime.asc()).count()
            else:
                rows=self.session.query(TActivity).filter_by(userid=userid,activityname=activityname).order_by(TActivity.starttime.asc())
                count=self.session.query(TActivity).filter_by(userid=userid,activityname=activityname).order_by(TActivity.starttime.asc()).count()
            if count ==0:
                return None,None
                #----在此終結----
            
            dateList=[]
            actidList=[]
            
            for act in rows:
                date=act.starttime
                result=date.split('T')
                f_date = time.strptime(date.split('T')[0], "%Y-%m-%d")
                datestring="{0}-{1:02d}-{2:02d}".format(f_date.tm_year,f_date.tm_mon,f_date.tm_mday)
                dateList.append(datestring)
                actidList.append(act.activityid)
            length=len(dateList)
            startIndex=0
            if length>=12:
                startIndex=length-12
            days=[]
            actid=[]
            
            
            for i in range(startIndex,length):
                days.append(dateList[i])
                actid.append(actidList[i])
            return days,actid 
        #---更新用---
       
        def update_facility(self,fac):
            try:
                value =self.session.query(TFacility).filter_by(facilityid=fac.facilityid).first()                
                value.name            =  fac.name         
                value.deviceids       =  fac.deviceids    
                value.phone           =  fac.phone        
                value.address         =  fac.address      
                value.email           =  fac.email        
                value.group           =  fac.group        
                value.vender          =  fac.vender       
                value.registertime    =  fac.registertime
                
                self.session.flush()
                self.session.commit()
            except:
                print('Error in def update_state')
        def update_userinfo(self,user):
            try:
                value =self.session.query(TUserInfo).filter_by(userid=user.userid).first()                
                
                value.realname    =   user.realname  
                value.nationalid  =   user.nationalid
                value.birthday    =   user.birthday  
                value.disease     =   user.disease   
                value.height      =   user.height    
                value.weight      =   user.weight    
                value.gender      =   user.gender    
                value.phone       =   user.phone     
                value.facilityid  =   user.facilityid
                value.status      =   user.status    
                value.deviceid    =   user.deviceid  
                value.note        =   user.note      
                value.therapist   =   user.therapist 
                value.patientid     =user.patientid
                value.trainingmode  =user.trainingmode
                
                value.duration      =user.duration
                value.registertime  =user.registertime
                self.session.flush()
                self.session.commit()
            except:
                print('Error in def update_userinfo')
                
        def update_activity(self,act):
            try:
                value =self.session.query(TActivity).filter_by(activityid=act.activityid).first()        
                value.userid      =act.userid      
                value.facilityid  =act.facilityid  
                value.activityname=act.activityname
                value.starttime   =act.starttime   
                value.duration    =act.duration    
                value.score       =act.score       
                value.scoreACT    =act.scoreACT    
                value.status      =act.status      
                value.jointid     =act.jointid
                
                self.session.flush()
                self.session.commit()
            except:
                print('Error in def update_activity')
        def update_user_status(self,userid,status):
            try:
                value =self.session.query(TUserInfo).filter_by(userid=userid).first()
                value.status=status
                self.session.flush()
                self.session.commit()
            except:
                print('Error in update_user_userstatus')
                
        def update_user_device(self,userid,deviceid):
            try:
                value =self.session.query(TUserInfo).filter_by(userid=userid).first()                
                value.deviceid=deviceid
                self.session.flush()
                self.session.commit()
            except:
                print('Error in update_user_device')
        def update_activity_userid(self,activityid,userid):
            try:
                value =self.session.query(TActivity).filter_by(activityid=activityid).first()        
                value.userid=userid
                self.session.flush()
                self.session.commit()
            except:
                print('Error in update_activity_userid')