import json
from datetime import datetime
folder="D:\\Dropbox\\tmpp202301\\goodbackup\\"
class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
def testdisp_database():
    
    return "測試是否進入網站"
def export_class(item,filename="typename"):
    file = open(filename+".txt", "w",encoding='UTF-8')
    for f in item:
        dictionary=f.__dict__
        dictionary.pop('_sa_instance_state', None)
        str=json.dumps(dictionary,  ensure_ascii=False, cls=DatetimeEncoder)
        file.writelines(str+"\n")
    file.close()

from apps.authentication.models import TFacility,TEvent,TCustomer,TProject,TDevice,Users

def crm_database():

    export_class(Users.query.all(),"users")    
    export_class(TFacility.query.all(),"tfacility")
    export_class(TEvent.query.all(),"TEvent")
    export_class(TCustomer.query.all(),"tcustomer")
    
    string="done"
    return string
def get_lines_read(filename):
    fp = open(filename, "r",encoding='UTF-8')
    lines=fp.readlines()
    fp.close()
    return lines


##---CRM的導入
def crm_read():
    global folder
    
    #---載入Users-------
    lines=get_lines_read(folder+"users.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("customerList")
        dic.pop("facilityList")
        fac=Users()
        fac.add_new(dic)
        fac.password=fac.password.encode()
        db.session.add(fac)
        #print(lines[i],type(dic),",類別:",type(fac))
    #---載入TFacility-------
    lines=get_lines_read(folder+"tfacility.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        
        fac=TFacility(dic)
        db.session.add(fac)

    #---載入TCustomer-------    
    lines=get_lines_read(folder+"tcustomer.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("facilityid")
        fac=TCustomer(dic)
        db.session.add(fac)
        
    #---載入TEvent-------
    lines=get_lines_read(folder+"tevent.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("ownerid")
        dic.pop("facilityid")
        dic.pop("customerList")
        
        
        try:
            datetime.strptime(dic['endtime']   , '%Y-%m-%d %H:%M:%S')#'2022-05-13 07:24:00'
            datetime.strptime(dic['starttime'] , '%Y-%m-%d %H:%M:%S')
            datetime.strptime(dic['nexttime']  , '%Y-%m-%d %H:%M:%S')
        except:
            print("not meet")
        
        try:
            dic['endtime']     =datetime.strptime(dic['endtime']   , '%Y-%m-%d %H:%M:%S')#'2022-05-13 07:24:00'
            dic['starttime']   =datetime.strptime(dic['starttime'] , '%Y-%m-%d %H:%M:%S')
            dic['nexttime']    =datetime.strptime(dic['nexttime']  , '%Y-%m-%d %H:%M:%S')
        except:
            print("not right item")
        fac=TEvent(dic)
        db.session.add(fac)

    db.session.commit()
    return "done"
def crm_user_password():
    global folder
    
    #---載入Users-------
    lines=get_lines_read(folder+"users.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("customerList")
        dic.pop("facilityList")
        print("Type:",type(dic["password"]),",content:",dic["password"])
        user=Users.query.filter(Users.id==dic["id"]).first()
        user.password=dic["password"].decode()
        #fac=Users()
        #fac.add_new(dic)
        #fac.password=fac.password.encode()
        #db.session.add(fac)
        #print(lines[i],type(dic),",類別:",type(fac))

from apps import db

def show_all(the_class):
    for c in the_class:
        print(type(c),"->",c)
    return
def create_test01():


    
    dic={"id":1,"name":"陳英豪","phone":"0922129123","email":"ray@longgood","title":"大帥帥"}
    customer=TCustomer(dic)
    db.session.add(customer)

    dic={"id":2,"name":"陳淫豪","phone":"0922129123","email":"ray@longgood","title":"大帥帥"}
    customer=TCustomer(dic)
    db.session.add(customer)

    
    dic={"id":3,"name":"陳盈豪","phone":"0922129123","email":"ray@longgood","title":"大帥帥"}
    customer=TCustomer(dic)
    db.session.add(customer)

    
    
    dic={"id":1,"name":"臺大醫院","address":"台北市人見人愛路1001"}
    facility=TFacility(dic)
    db.session.add(facility)
    
    dic={"id":2,"name":"臺中醫院","address":"台北市人見可愛路1001"}
    facility=TFacility(dic)
    db.session.add(facility)
    
    
    
    dic={"id":3,"name":"臺小醫院","address":"台北市人見不愛路1001"}
    facility=TFacility(dic)
    db.session.add(facility)
    
    
    
    db.session.commit()
    
    return
def relation_test01():
    
    customer=TCustomer.query.filter(TCustomer.id==2).first()
    if customer:
        customer.name="我是老二大"
        customer.fid=3
        db.session.flush()
        db.session.commit()
        print("更新完成")
    else:
        print("沒找到!")
    
def relation_test02():
    
    fac=TFacility.query.filter(TFacility.id==2).first()
    customer=TCustomer.query.filter(TCustomer.id==3).first()
    if fac:
        customer.name="我改改3"
        fac.name="藏雲閣2"
        fac.add_to_customer.append(customer)
        db.session.flush()
        db.session.commit()
        print("更新完成")
    else:
        print("沒找到!")
def create_test02():
    dic={"id":1,"description":"我見了面","nextstep":"繼續見面"}
    visiting=TEvent(dic)
    db.session.add(visiting)
    
    dic={"id":2,"description":"搭訕","nextstep":"約出來見面"}
    visiting=TEvent(dic)
    db.session.add(visiting)    
    
    
    db.session.commit()
def relation_test03():
    
    vis=TEvent.query.filter(TEvent.id==2).first()
    cust=TCustomer.query.filter(TCustomer.id==1).first()
    if vis:
        cust.name="我改-多對多"
        vis.description="我見了某人"
        vis.customer.append(cust)
        db.session.flush()
        db.session.commit()
        print("更新完成")
    else:
        print("沒找到!")
import re
def connect_relation_event():
    lines=get_lines_read(folder+"tevent.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        ownerid     =dic["ownerid"]
        #customerList=int(dic["customerList"].sub(";"))
        customerList = int(re.sub(";","",dic["customerList"]))
        facilityid  =dic["facilityid"]
        
        dic.pop("ownerid")
        dic.pop("facilityid")
        dic.pop("customerList")
        cust=TCustomer.query.filter_by(id=customerList).first()
        
        
        id=dic["id"]
        event=TEvent.query.filter_by(id=id).first()
        event.userID=int(ownerid)
        event.facilityID=int(facilityid)
        event.customerList.append(cust)
    db.session.flush()
    db.session.commit()
    """
    TEvent.query.all()
    for c in the_class:
    """ 
    return
def connect_relation_customer():
    lines=get_lines_read(folder+"tcustomer.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        facilityid=dic["facilityid"]
        
        dic.pop("facilityid")
        id=dic["id"]
        customer=TCustomer.query.filter_by(id=id).first()
        customer.facilityID=facilityid
    db.session.flush()
    db.session.commit()
    

def rela_test():


    ##01CRM原始類別讀入，並去除不需的變數
    #crm_read()
    ##02建立類別間的關聯，一樣從原始文字檔讀取。
    #connect_relation_event()
    #connect_relation_customer()
    ##03依序檢查TEvent-Facility,userID,customerList
    
    
    print("-----------------------")
    #show_all(TCustomer.query.all())
    
    #show_all(TFacility.query.all())
    #show_all(TEvent.query.all())
    #show_all(Users.query.all())
    ##04更新使用者的密碼:
    crm_user_password()

    return "關聯我"