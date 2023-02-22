from apps.authentication.models import TFacility,TEvent,TProject,TDevice,TManager,TCustomer, TUser, TActivity,TDevice
import json
from datetime import datetime
from apps.authentication.util import hash_pass
from apps import db

folder="D:\\Dropbox\\tmpp202301\\goodbackup\\"
foldermj="D:\\Dropbox\\tmpp202301\\majestybackup\\"
class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
def backup_read():
    #read_cloudcrm()
    read_tuser(["tuserinfo-majesty20230221.json","tuserinfo-kao20230221.json","tuserinfo-tmu20230221.json","tuserinfo-yuan20230221.json"])
    #crm_readtactivity()
    #crm_readtmanager()
    #crm_readtfacility()
    #crm_readtuserupdate()
    #crm_readdevice()
    #crm_read_user_sqlite("tuserinfo-yuan.txt")
    #crm_read_activity_sqlite("tactivity-yuan.txt")
    return "純讀取"
def read_cloudcrm():
    print("讀取原有CRM")
    global folder
    
    #---載入Users-------
    lines=get_lines_read(folder+"usersModify.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("customerLIST")
        dic.pop("facilityLIST")

        fac=TManager(dic)
        db.session.add(fac)
    db.session.commit()
    #---載入TFacility-------
    lines=get_lines_read(folder+"tfacilityModify.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("id")      
        
        fac=TFacility(dic)
        db.session.add(fac)

    db.session.commit()
    #---載入TCustomer-------    
    lines=get_lines_read(folder+"tcustomerModify.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("facilityID")
        dic.pop("activityList")
        dic.pop("id")
        dic.pop("department")
        dic.pop("managerID")
        dic.pop("submanagers")
        
        
        fac=TCustomer(dic)
        db.session.add(fac)
        
    db.session.commit()
    #---載入TEvent-------
    lines=get_lines_read(folder+"teventModify.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])

        dic.pop("facilityID")
        dic.pop("customerID")
        dic.pop("managerID")
        dic.pop("id")        
        
        try:
            datetime.strptime(dic['endTime']   , '%Y-%m-%d %H:%M:%S')#'2022-05-13 07:24:00'
            datetime.strptime(dic['startTime'] , '%Y-%m-%d %H:%M:%S')
            datetime.strptime(dic['nextTime']  , '%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        try:
            dic['endTime']     =datetime.strptime(dic['endTime']   , '%Y-%m-%d %H:%M:%S')#'2022-05-13 07:24:00'
            dic['startTime']   =datetime.strptime(dic['startTime'] , '%Y-%m-%d %H:%M:%S')
            dic['nextTime']    =datetime.strptime(dic['nextTime']  , '%Y-%m-%d %H:%M:%S')
        except:
            pass
        fac=TEvent(dic)
        db.session.add(fac)

    db.session.commit()

def get_json_read(filename,error_term=None,new_term=None):
    
    with open(filename, encoding='utf-8') as fh:
        result=fh.read()#lines = f.readlines()
        if error_term:
            for i in range(0,len(error_term)):
                result=result.replace(error_term[i],new_term[i])
        data=json.loads(result)    
    with open(filename+"-output.json", "w",encoding='utf-8') as fw:
        fw.write(result)
    return data
def get_json_LIST(fnames=[],error_term=None,right_term=None):    
    global foldermj
    #---載入TUser-------
    userLIST=[]
    for fname in fnames:
        print(fname)
        data=get_json_read(foldermj+fname,error_term,right_term)
        userLIST=userLIST+data["rows"]
    return userLIST
def read_tuser(fnames=[]):
    global foldermj
    print("載入TUserInfo")
    #---載入TUser-------
    error_term=["Male,","Female,","Neutral,","N,","Femal,","女性,",": ,",": None,"]
    right_term=["\"Male\",","\"Female\",","\"Neutral\",","\"Neutral\",","\"Female\",","\"Female\",",": \"None\",",": \"None\","]
    userLIST=get_json_LIST(fnames,error_term,right_term)
    
    for user in userLIST:
        print(user["realname"])
    return
"""
    userid=0
    realname=1
    nationalid=2
    birthday=3
    disease=4
    trainingmode=5
    height=6
    weight=7
    gender=8
    phone=9
    facilityid=10
    therapist=11
    note=12
    patientid=13
    status=14
    deviceid=15
    duration=16
    registertime=17
    messenger=18

    for i in range(1,10):#len(lines)):
        dic=lines[i].split(";")
        #dic=json.loads(lines[i])
        user={}
        user["gender"]=detect_gender(dic[gender])
        user["accountId"]=dic[userid]
        user["localPhone"]=dic[phone]
        user["birthday"]=detect_datetime(dic[birthday])
        
        user["height"]=dic[height]
        user["weight"]=dic[weight]
        user["messengerId"]=""
        user["realName"]=dic[realname]
        user["nationalId"]=dic[nationalid]
        user["chartNumber"]=dic[patientid]
        user["doctorAdvise"]=detect_none(dic[note])+detect_none(dic[disease])
        user["uploadStatus"]=dic[status]
        #user["deviceID"]=dic[deviceid"]
        if dic[disease] is not None:

            if "健康" in dic[disease] or "Healthy" in dic[disease] or "自立" in dic[disease] or "元氣" in dic[disease]:   
                user["diseaseIndex"]=1
            elif "中風" in dic[disease] or "Stroke" in dic[disease] or "脳卒" in dic[disease]:
                user["diseaseIndex"]=2
            elif "帕金森氏症" in dic[disease] or "Parkin" in dic[disease] or "PD" in dic[disease]:
                user["diseaseIndex"]=3            
            elif "衰老" in dic[disease] or "Senescence" in dic[disease]:
                user["diseaseIndex"]=4            
            elif "高齡" in dic[disease] or "高齢" in dic[disease]:
                user["diseaseIndex"]=5
            elif "膝關節置換" in dic[disease] or "Knee" in dic[disease]:
                user["diseaseIndex"]=6
            elif "五十肩" in dic[disease] or "Frozen" in dic[disease]:
                user["diseaseIndex"]=7 
            elif "網球肘" in dic[disease] or "elbow" in dic[disease]:
                user["diseaseIndex"]=8
            elif "神經炎" in dic[disease] or "Neuritis" in dic[disease]:
                user["diseaseIndex"]=9
            elif "麻木" in dic[disease] or "Numbness" in dic[disease]:
                user["diseaseIndex"]=10            
            elif "肌少症" in dic[disease] or "肌肉無力" in dic[disease] or "Muscle weakness" in dic[disease]:
                user["diseaseIndex"]=11
            elif "失眠" in dic[disease] or "Insomnia" in dic[disease]:
                user["diseaseIndex"]=12
            elif "乳癌" in dic[disease] or "CA Breast" in dic[disease]:
                user["diseaseIndex"]=13    
            elif "COVID" in dic[disease] or "新冠" in dic[disease]:
                user["diseaseIndex"]=14   
            elif ("貧血" in dic[disease]) or ("anemia" in dic[disease]) or ("Anemia" in dic[disease]):
                user["diseaseIndex"]=15 
            elif "介護" in dic[disease]:
                user["diseaseIndex"]=20   
            elif "支援" in dic[disease]:
                user["diseaseIndex"]=21   
            else:
                user["diseaseIndex"]=0
        theuser=TUser(user)
        print(user,"記錄使用者:",theuser)
        db.session.add(theuser)
    db.session.commit()
"""
def read_majesty_tactivity():
    global foldermj
    #---載入TActivity-------
    lines=get_lines_read(foldermj+"tactivity.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        act={}

        act["startTime"]=detect_fulltime(dic["starttime"])
        act["key"]=dic["activityid"]
        act["finishRate"]=dic["scoreACT"]
        act["duration"]=dic["duration"]        
        act["score"]=dic["score"]
        act["dispName"]=dic["activityname"]
        act["uploadStatus"]=dic["status"]
        act["jointId"]=dic["jointid"]
        act["productType"]=detect_actname(act["dispName"])
        theact=TActivity(act)
        db.session.add(theact)
    db.session.commit()

def export_class(item,filename="typename"):
    file = open(filename+".txt", "w",encoding='UTF-8')
    for f in item:
        dictionary=f.__dict__
        dictionary.pop('_sa_instance_state', None)
        str=json.dumps(dictionary,  ensure_ascii=False, cls=DatetimeEncoder)
        file.writelines(str+"\n")
    file.close()


def get_lines_read(filename):
    fp = open(filename, "r",encoding='UTF-8')
    lines=fp.readlines()
    fp.close()
    return lines
def detect_none(obj,number=0):
    result=""
    if type(obj)==str:
        if (obj != "null") and (obj!= "Null") and (obj!="NULL")and ("None" not in obj) and (obj!="NULLUSER") and (obj!="XXXX"):
            result=obj
        
    if number!=0:
        if result=="":
            result=number
    
    return result
def detect_gender(value):
    result=0
    if value is not None:
        if "Male" in value or "male" in value or "m" in value or "M" in value or "男" in value:  
            result=1
        elif "Female" in value or "female" in value or "femal" in value or "f" in value or "F" in value or "女" in value:
            result=2
        elif "Neu" in value or "neu" in value or "中" in value:
            result=0
        else:
            result=0
    
    return result
    
def detect_actname(value):
    result=0
    if value is not None:
        if "REBEST_PRO" in value:
            result=30000
        elif "REBEST_FREE" in value:
            result=20000
        elif "GAITSTRAIGHT" in value:
            result=51000
        elif "Single_" in value:
            result=10000
        elif "GAITFORWARD" in value:
            result=51001
        else:

            result=0
    else:
        result=-99999
def detect_datetime(value):
    result=datetime.now().date()
    if value is not None:
        if "/" in value:
            result=datetime.strptime(value,'%Y/%m/%d').date()
    return result        
import iso8601
def detect_fulltime(value):
    time=datetime.now()
    if value is not None:
        try:
            time=iso8601.parse_date(value)
            #time=datetime.datetime.fromisoformat(value)
            #time = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
            
            
        except:
            #print("無法解析:",value)
            if "-" in value:
                try:
                    #time = datetime.datetime.strptime(value, '%Y%m%d')
                    time = datetime.strptime(value, '%Y%m%d-%H%M%f')
                except:
                    print("橫槓解析不行",value.split("-")[0])
            elif "/" in value:
                try:
                    if " " in value:
                        time = datetime.strptime(value.split(" ")[0], '%m/%d/%Y')
                    else:
                        time = datetime.strptime(value, '%Y/%m/%d')
                except:
                    pass
            
                
    return time

def crm_readtuserupdate():
    global foldermj
    #---載入TUser-------
    lines=get_lines_read(foldermj+"tuserinfo.txt")
    userlist=[]
    userAdd=[]
    accountNumber=0
    count=0
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        user={}
        accountId=dic["userid"]
        

        if accountId not in userlist:
            userlist.append(accountId)
            accountNumber=accountNumber+1
        user=TUser.query.filter_by(accountId=accountId).first()
        if user:
            count=count+1
    print("from Raw:",accountNumber,",maria:",count)
    #---載入TManager中受其管理的患者-------
    lines=get_lines_read(foldermj+"tmanager.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        patients=dic["patients"]
        patientList=patients.split(";")
        for patient in patientList:
            if patient:
                if (not "XXXX" in patient) and (not "NULLUSER" in patient):
                    if not patient in userlist:
                        userlist.append(patient)
                        print("M:",patient)
                        userAdd.append(patient)
                else:
                    print("error:",patient)
    #---載入TActivity中受登記的患者-------
    lines=get_lines_read(foldermj+"tactivity.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        patient=dic["userid"]
        if patient:
            if (not "XXXX" in patient) and (not "NULLUSER" in patient):
                if not patient in userlist:
                    userlist.append(patient)
                    userAdd.append(patient)
    count=0
    for accountId in userAdd:
        user=TUser.query.filter_by(accountId=accountId).first()
        if user:
            
            count=count+1
        else:
            u=TUser({"accountId":accountId})
            u.accountId=accountId
            u.add_new()
    print(len(userAdd),"其中有",count,"在資料庫內。現已新增:",TUser.query.all())
    
    return
def crm_readtmanager():
    global foldermj
    #---載入TManager-------
    lines=get_lines_read(foldermj+"tmanager.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        manager={}
        manager["realName"]=dic["name"]
        manager["eMail"]=dic["email"]
        manager["localPhone"]=dic["phone"]
        manager["accountId"]=dic["username"]
        manager["password"]=dic["password"]
        manager["realName"]=dic["name"]
        
        manager["gender"]=detect_gender(dic["gender"])
        
        themanager=TManager(manager)
        db.session.add(themanager)
    db.session.commit()
def crm_readtfacility():
    global foldermj
    #---載入TFacility-------
    lines=get_lines_read(foldermj+"tfacility.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        facility={}
        facility["displayName"]=dic["name"]
        facility["address"]=dic["address"]
        facility["email"]=dic["email"]
        facility["group"]=dic["group"]
        facility["vender"]=dic["vender"]
        facility["key"]=dic["facilityid"]
        thefacility=TFacility(facility)
        db.session.add(thefacility)
    db.session.commit()            

def crm_readdevice():
    global foldermj
    facility=get_lines_read(foldermj+"tfacility.txt")
    facDic=modify_lines(facility)
    deviceidList=get_lines_attribute(facDic,"deviceids")
    
    activity=get_lines_read(foldermj+"tactivity.txt")
    actDic=modify_lines(activity)
    deviceidList=deviceidList+get_lines_attribute(actDic,"activityid")
    result=list(set(deviceidList))
    for r in result:
        if (len(r)!=10 and len(r)!=12 and len(r)!=18 and len(r)!=22) or ("@" in r):#GB8ZAGSLTP
            result.remove(r)
            
    removeList=["WlshospLiao","Developer","888888888788","AAEECC"]
    for r in removeList:
        if r in result:
            result.remove(r)
    for r in result:
        dev=TDevice()
        dev.mac=r
        db.session.add(dev)
    db.session.commit()
##---CRM的導入

    return "done"
def crm_user_password():
    global folder
    
    #---載入Users-------
    lines=get_lines_read(folder+"users.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dic.pop("customerList")
        dic.pop("facilityList")
        user=TManager.query.filter(TManager.uid==dic["id"]).first()
        
        
        if user.uid==0:
            print("0 ray:",user.realname,"end name")
            user.password=hash_pass("rraayy")
        elif user.uid==1:
            print("1:",user.userid,"end name")
            user.password=hash_pass("rraayy")
        elif user.uid==2:
            print("2",user.userid,"end name")
            user.password=hash_pass("rraayy")
        elif user.uid==3:
            print("3",user.userid,"end name")
            user.password=hash_pass("54158175")
        
        db.session.flush()
    db.session.commit()
def crm_read_user_sqlite(filename):
    #讀取來自元保宮的資料
    global foldermj
    #---載入TUser-------
    lines=get_lines_read(foldermj+filename)
    for i in range(len(lines)):
        dic=lines[i].split(";")
        #print(dic)
        user={}
        user["gender"]=detect_gender(dic[9])
        user["accountId"]=dic[0]
        user["realName"]=dic[2]
        user["birthday"]=detect_datetime(dic[4])
        user["nationalId"]=dic[3]
        
        theuser=TUser(user)
        
        result=TUser.query.filter_by(accountId=user["accountId"]).all()
        if result:
            pass
        else:
            theuser=TUser(user)
            db.session.add(theuser)
    db.session.commit()
    return
def crm_read_activity_sqlite(filename):
    #讀取來自元保宮的活動資料
    global foldermj
    #---載入TUser-------
    lines=get_lines_read(foldermj+filename)
    
    #for i in range(100):
    
    for i in range(len(lines)):
        dic=lines[i].split(";")

        act={}
        act["key"]=dic[0]
        act["productType"]=detect_actname(dic[3])
        
        act["startTime"]=detect_fulltime(dic[4])
        try:
            act["score"]=float(dic[6])
        except:
            act["score"]=0
        
        result=TActivity.query.filter_by(key=act["key"]).all()
        if result:
            pass
            #print(act["key"],":",result)
        else:
            theact=TActivity(act)
            db.session.add(theact)
        
        
    db.session.commit()
    return




import re
def modify_lines(lines):
    dics=[]
    
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        dics.append(dic)
    return dics
##====
def get_lines_attribute(dics,attribute):
    count=0
    result=None
    attList=[]
    if dics is None:
        print("查無!")
        return attList
    for dic in dics:
        if attribute in dic:
            try:
                tmp=dic[attribute]
                
                
                
                if (tmp is not None) and (tmp is not "NULL") and (tmp is not "None") and ("NULL" not in tmp) and ("ull" not in tmp) and (tmp is not ""):
                
                    if "_" in tmp:
                        t=tmp.split("_")[0]
                        attList.append(t)
                    elif ";" in tmp:
                        tmps=tmp.split(";");
                        for t in tmps:
                            if len(t)>0:
                                attList.append(t)
                    else:            
                        attList.append(tmp)
                        
            except:
                print("get lines attribute fail")
                pass
        

    if "None" in attList:
        attList.remove("None")
    if "" in attList:
        attList.remove("")
    if 'None' in attList:
        attList.remove('None')
    return attList

#有兩種查詢模式，主要是根據value是否為多項-
def query_lines(dics,attribute, value="",deltalen=0):
    result=None
    count=0
    index=count
    
    if dics is None:
        print("查無!!!!!!!")
        return None,-99
    
            
    
    
    #--------多個模式--------------
    #print("--query_lines:",value)
    if ";" in str(value):

        values=value.split(";")
        #print("in value:",value,",len:",len(values))
        
        resultList=[]
        indexList=[]
        for v in values:
        
            for dic in dics:
                count=count+1

                if str(dic[attribute])==str(v):
                    resultList.append(dic)
                    indexList.append(count)
                    break;
        return resultList,indexList
    elif len(str(value))<1:
        return None,None
    else:
        #--------單一模式--------------

        for dic in dics:
            count=count+1
            if dic[attribute]==value:
                result=dic
                index=count
                break
        return result,index

    
import random


def mysql01_build_facility():
    #--手動建立元保宮
    facilityList=["803253C72E96","A85E4538610C"]
    for fkey in facilityList:
        f=TFacility.query.filter_by(key=fkey).first()
        if not f:
            newfac=TFacility()
            newfac.key=fkey
            newfac.displayName="中國醫元保宮"
            db.session.add(newfac)
    db.session.commit()
    #--從tapifacility建立facility 取得tapifacility內的mac碼，還建立TFacility
    
    
    sql="select mac from tapifacility"
    macresult=db.engine.execute(sql).fetchall()
    macLIST=[]
    count=0
    
    
    
    result="機構現況:<br>"
    for r in macresult:
        if len(r[0])>0:
            facs=TFacility.query.filter(TFacility.key.like(r[0]+"%")).all()
            if facs:
                for f in facs:
                    pass
                    #result=result+"TapiFmac:{0}=>TFkey:{1}<br>".format(r[0],f.key)
            else:
                count=count+1
                if r[0] not in macLIST:
                    macLIST.append(r[0])
    for mac in macLIST:
        #在這邊新增機構
        sql="SELECT * FROM `TapiFacility` WHERE `mac`=\"{0}\"".format(mac)
        apifacs=db.engine.execute(sql).fetchall()
        for apifac in apifacs:
            resultstr="結果:mac:{0},{1},{2},{3},{4},{5},{6}<br>".format(apifac[0],apifac[1],apifac[2],apifac[3],apifac[4],apifac[5],apifac[6])
            result=result+resultstr
                
    return "待新增Facility數量:"+str(count)+",maclen:"+str(len(macLIST))+"<br>"+result
    """
    "314BBC8C7694"
    很厲害的寫法
    sql="select mac from tapifacility"
    result=db.engine.execute(sql).fetchall()
    devLIST=[]
    for r in result:
        dev=TUser.query.filter(TUser.accountId.like(r[0]+"%")).all()
        #dev=TDevice.query.filter_by(mac=r[0]).all()
        for d in dev:
            if d not in devLIST:
                devLIST.append(d.accountId)
    """
def mysql02_build_userfacility():
    users=TUser.query.filter(TUser.facilityID.is_(None)).all()
    return str(users)
def testdisp_database():
    """
    很厲害的寫法
    sql="select mac from tapifacility"
    result=db.engine.execute(sql).fetchall()
    devLIST=[]
    for r in result:
        dev=TUser.query.filter(TUser.accountId.like(r[0]+"%")).all()
        #dev=TDevice.query.filter_by(mac=r[0]).all()
        for d in dev:
            if d not in devLIST:
                devLIST.append(d.accountId)
    """
    sql="select mac from tapifacility"
    result=db.engine.execute(sql).fetchall()
    devLIST=[]
    for r in result:
        dev=TUser.query.filter(TUser.accountId.like(r[0]+"%")).all()
        #dev=TDevice.query.filter_by(mac=r[0]).all()
        for d in dev:
            if d not in devLIST:
                devLIST.append(d.accountId)
    
    return str(devLIST)