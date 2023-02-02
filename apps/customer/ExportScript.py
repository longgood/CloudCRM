import json
class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
def export_class(item,filename="typename"):
    file = open(filename+".txt", "w",encoding='UTF-8')
    for f in item:
        dictionary=f.__dict__
        dictionary.pop('_sa_instance_state', None)
        str=json.dumps(dictionary,  ensure_ascii=False, cls=DatetimeEncoder)
        file.writelines(str+"\n")
    file.close()

from apps.authentication.models import TFacility,TVisiting,TCustomer,TProject,TDevice,Users

def crm_database():

    export_class(Users.query.all(),"users")    
    export_class(TFacility.query.all(),"tfacility")
    export_class(TVisiting.query.all(),"TVisiting")
    export_class(TCustomer.query.all(),"tcustomer")
    
    string="done"
    return string
def crm_read():
    filename="D:\\_Projects\\CloudCRM\\tfacility.txt"
    fp = open(filename, "r",encoding='UTF-8')
    lines=fp.readlines()
    fp.close()
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        fac=TFacility(dic)
        print(lines[i],type(dic),",類別:",type(fac))
        
    return lines
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
    visiting=TVisiting(dic)
    db.session.add(visiting)
    
    dic={"id":2,"description":"搭訕","nextstep":"約出來見面"}
    visiting=TVisiting(dic)
    db.session.add(visiting)    
    
    
    db.session.commit()
def relation_test03():
    
    vis=TVisiting.query.filter(TVisiting.id==2).first()
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
def rela_test():
    
    #create_test02()
    #relation_test03()
    
    show_all(TCustomer.query.all())
    show_all(TFacility.query.all())
    show_all(TVisiting.query.all())
    
    
    
    return "done"