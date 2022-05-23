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
        value="姓名:'%s',id='%s',userid='%s',  職稱:'%s'" % (
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
    def check_key(self,dic,key):
       
        result=None
        try:
            result=dic[key]
            if result == "NULLUSER":
                result=None
        except KeyError:
            result=None
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
                self.id          = self.check_key(  dic,"id") 
                self.ownerid    = self.check_key(  dic,"ownerid")  
                self.name  = self.check_key(  dic,"name")  
                self.phone    = self.check_key(  dic,"phone") 
                self.cellphone     = self.check_key(  dic,"cellphone") 
                self.lineid      = self.check_key(  dic,"lineid") 
                self.email      = self.check_key(  dic,"email")  
                self.activityList      = self.check_key(  dic,"activityList")  
                self.facilityid       = self.check_key(  dic,"phone") 
                self.department  = self.check_key(  dic,"department")  
                self.title      = self.check_key(  dic,"title")  
                self.submanagers    = self.check_key(  dic,"submanagers")  
            db.session.add(self)
            db.session.commit()
            result=True
        else:
            print("---重複產出----")
        return result
    def __init__(self):
        return
    def __repr__(self):
        return "Customer(id='%s', 名稱:'%s', 職稱:'%s'" % (
                   self.id, self.name, self.title) 
        
    
class TFacility(db.Model):
    __tablename__ = 'TFacility'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    address=db.Column(db.String(64))
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
    def check_key(self,dic,key):
       
        result=None
        try:
            result=dic[key]
            if result == "NULLUSER":
                result=None
        except KeyError:
            result=None
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
        return "Facility(id='%s', 名稱:'%s', 地址:'%s'" % (
                   self.id, self.name, self.address)
#每一次地拜訪或是會晤都算是一個TActivity->多個TActivity組成一個TProjects
class TActivity(db.Model):

    __tablename__ = 'TActivity'
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
    def check_key(self,dic,key):
       
        result=None
        try:
            result=dic[key]
            if result == "NULLUSER":
                result=None
        except KeyError:
            result=None
        return result
    def add_new(self,dic=None):
    
        result=False
        if dic:
            id=self.check_key(  dic,"userid")
        else:
            id=self.id
        if id is None:
            print("錯誤ID",dic["userid"])
            return result
        
        act=TActivity.query.filter_by(id=id).first()
        if not act:
            if dic:
                self.id             = self.check_key(  dic,"id") 
                self.ownerid        = self.check_key(  dic,"ownerid")  
                self.facilityid     = self.check_key(  dic,"facilityid")  
                self.customerList   = self.check_key(  dic,"customerList") 
                self.starttime      = self.check_key(  dic,"starttime") 
                self.endtime        = self.check_key(  dic,"endtime") 
                self.nexttime       = self.check_key(  dic,"nexttime")  
                self.type           = self.check_key(  dic,"type")  
                self.description    = self.check_key(  dic,"description") 
                self.nextstep       = self.check_key(  dic,"nextstep")  
                self.recommand      = self.check_key(  dic,"recommand")  
            db.session.add(self)
            db.session.commit()
            result=True
        else:
            print("---重複產出----")
        return result
    
    def update(self):
        try:
            db.session.flush()
            db.session.commit()
        except:
            print("--error--")
    def __init__(self, **kwargs):
        self.customerList=""
        return
    def __repr__(self):
        
        return "<TActivity(id='%s',醫院公司:'%s' 顧客們='%s', 起始時間='%s',結束時間:'%s'description='%s')>" % (
                   self.id,self.facilityid, self.customerList, self.starttime,self.endtime,self.description)
                   

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
    
    def __init__(self):
        return
    def __repr__(self):
        return
@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    userid = request.form.get('userid')
    user = Users.query.filter_by(userid=userid).first()
    return user if user else None
