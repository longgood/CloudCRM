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
def export_class(item,filename="typename"):
    file = open(filename+".txt", "w",encoding='UTF-8')
    for f in item:
        dictionary=f.__dict__
        dictionary.pop('_sa_instance_state', None)
        str=json.dumps(dictionary,  ensure_ascii=False, cls=DatetimeEncoder)
        file.writelines(str+"\n")
    file.close()



def crm_database():

    #export_class(Users.query.all(),"users")    
    export_class(TFacility.query.all(),"tfacility")
    export_class(TEvent.query.all(),"TEvent")
    #export_class(TCustomer.query.all(),"tcustomer")
    
    string="done"
    return string
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
def crm_readtuser():
    global foldermj
    #---載入TUser-------
    lines=get_lines_read(foldermj+"tuserinfo.txt")
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        user={}
        user["gender"]=detect_gender(dic["gender"])
        user["accountId"]=dic["userid"]
        user["localPhone"]=dic["phone"]
        user["birthday"]=detect_datetime(dic["birthday"])
        
        user["height"]=dic["height"]
        user["weight"]=dic["weight"]
        user["messengerId"]=""
        user["realName"]=dic["realname"]
        user["nationalId"]=dic["nationalid"]
        user["chartNumber"]=dic["patientid"]
        user["doctorAdvise"]=detect_none(dic["note"])+detect_none(dic["disease"])
        user["uploadStatus"]=dic["status"]
        #user["deviceID"]=dic["deviceid"]
        if dic["disease"] is not None:

            if "健康" in dic["disease"] or "Healthy" in dic["disease"] or "自立" in dic["disease"] or "元氣" in dic["disease"]:   
                user["diseaseIndex"]=1
            elif "中風" in dic["disease"] or "Stroke" in dic["disease"] or "脳卒" in dic["disease"]:
                user["diseaseIndex"]=2
            elif "帕金森氏症" in dic["disease"] or "Parkin" in dic["disease"] or "PD" in dic["disease"]:
                user["diseaseIndex"]=3            
            elif "衰老" in dic["disease"] or "Senescence" in dic["disease"]:
                user["diseaseIndex"]=4            
            elif "高齡" in dic["disease"] or "高齢" in dic["disease"]:
                user["diseaseIndex"]=5
            elif "膝關節置換" in dic["disease"] or "Knee" in dic["disease"]:
                user["diseaseIndex"]=6
            elif "五十肩" in dic["disease"] or "Frozen" in dic["disease"]:
                user["diseaseIndex"]=7 
            elif "網球肘" in dic["disease"] or "elbow" in dic["disease"]:
                user["diseaseIndex"]=8
            elif "神經炎" in dic["disease"] or "Neuritis" in dic["disease"]:
                user["diseaseIndex"]=9
            elif "麻木" in dic["disease"] or "Numbness" in dic["disease"]:
                user["diseaseIndex"]=10            
            elif "肌少症" in dic["disease"] or "肌肉無力" in dic["disease"] or "Muscle weakness" in dic["disease"]:
                user["diseaseIndex"]=11
            elif "失眠" in dic["disease"] or "Insomnia" in dic["disease"]:
                user["diseaseIndex"]=12
            elif "乳癌" in dic["disease"] or "CA Breast" in dic["disease"]:
                user["diseaseIndex"]=13    
            elif "COVID" in dic["disease"] or "新冠" in dic["disease"]:
                user["diseaseIndex"]=14   
            elif ("貧血" in dic["disease"]) or ("anemia" in dic["disease"]) or ("Anemia" in dic["disease"]):
                user["diseaseIndex"]=15 
            elif "介護" in dic["disease"]:
                user["diseaseIndex"]=20   
            elif "支援" in dic["disease"]:
                user["diseaseIndex"]=21   
            else:
                user["diseaseIndex"]=0
        
        #if "_" in user["accountId"]:
            #print(user)
        theuser=TUser(user)
        
        db.session.add(theuser)
    db.session.commit()
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
def crm_readtactivity():
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
def crm_read():
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

def backup_read():
    crm_read()
    crm_readtuser()
    crm_readtactivity()
    crm_readtmanager()
    crm_readtfacility()
    crm_readtuserupdate()
    crm_readdevice()
    crm_read_user_sqlite("tuserinfo-yuan.txt")
    crm_read_activity_sqlite("tactivity-yuan.txt")
    return "純讀取"


##----------------------
##從主類別去搜尋並建立關聯關係
##----------------------
def connect_relation_facility():

    ###---001讀取原始的類別資料以及相關資料的RAW檔, 在此主角是TFacility, 關聯的類別為manager, subfacility---------------
    global foldermj
    #---載入TManager-------
    lines       =get_lines_read(foldermj+"tfacility.txt")
    
    managers    =get_lines_read(foldermj+"tmanager.txt")    
    subfacilitys=get_lines_read(foldermj+"tfacility.txt")
    
    managerDic=modify_lines(managers)
    subfacilityDic=modify_lines(subfacilitys)

    print("從檔案來的tmanager",len(managerDic))
    for i in range(len(lines)):
        ###---002找到該類別RAW檔中所定義的關聯關係ID，並據此去搜尋該類別在mariaDB內的uid---------------
        dic=json.loads(lines[i])
        key            =dic["facilityid"]
        managerIDs      =detect_none(dic["managerid"],"")
        subfacilityIDs  =detect_none(dic["subfacility"],"")
        #deviceIDs       =detect_none(dic["deviceids"],"")        
        
        #--從原本的csv去找

        mdics,mindexs     =query_lines(managerDic,"id",managerIDs)
        sfdics,sfindexs   =query_lines(subfacilityDic,"facilityid", subfacilityIDs)
        #ddics,dindexs     =query_lines(deviceDic,"deviceid", deviceIDs)
        #--這邊因為原先設定關係，會是多個subfacility, 以及多個管理者
        
        #--從資料庫來找
        facility=TFacility.query.filter_by(key=key).first()
        if facility:
            ##---多對多中，由TManager來發起新增。
            if mdics:
                
                for m in mdics:
                    accountId=m["username"]
                    mana=TManager.query.filter_by(accountId=accountId).first()
                    if mana:
                        mana.facilityLIST.append(facility)
            
            
            
            ##--分派上下從屬的關係。
            if sfdics:
                
                for sf in sfdics:
                    fid=sf["facilityid"]
                    subfaci=TFacility.query.filter_by(key=fid).first()
                    subfaci.bossID=facility.uid
                
    db.session.flush()
    db.session.commit()
    """
    TEvent.query.all()
    for c in the_class:
    """ 
    return
def connect_relation_manager():

    ###---001讀取原始的類別資料以及相關資料的RAW檔, 在此主角是TManager, 關聯的類別為user, manager, activity---------------,其中TFacility已經設定過了所以省略
    global foldermj
    #---載入TManager-------
    lines       =get_lines_read(foldermj+"tmanager.txt")
    
    submanagers    =get_lines_read(foldermj+"tmanager.txt")    
    users=get_lines_read(foldermj+"tuserinfo.txt")
    activitys=get_lines_read(foldermj+"tactivity.txt")
    
    
    submanagerDic=modify_lines(submanagers)
    usersDic=modify_lines(users)
    activityDic=modify_lines(activitys)
    
    print("從檔案來的tmanager",len(submanagerDic))
    for i in range(len(lines)):
        ###---002找到該類別RAW檔中所定義的關聯關係ID，並據此去搜尋該類別在mariaDB內的uid---------------
        dic=json.loads(lines[i])
        accountId=dic["username"]
        #-------------先找出原始TManager中，紀載跟各類別相關的物件---
        submanagerIDs       =detect_none(dic["submanager"],"")
        userIDs             =detect_none(dic["patients"],"")
        #activityIDs         =detect_none(dic["deviceids"],"")        
        
        
        #--TManager(csv)內的對應數值作為輸入值，到其他類別找到對應該資料的整個類別(實作)
        #例,tmanager有個欄位叫做submanager, 在tmanager內對應的欄位叫做id. 在mariaDB中對應搜尋的attribute是accountId
        #例,tmanager有個欄位叫做patients以分號隔開紀錄多組userid, 在tuserinfo內有個對應欄位也叫做userid, 314BBC8C76941000019592,新的格式(mariaDB)中User.accountId
        
        smdics,smindexs     =query_lines(submanagerDic,"id",submanagerIDs)
        udics,uindexs       =query_lines(usersDic,"userid", userIDs)

        
        #--從資料庫來找
        manager=TManager.query.filter_by(accountId=accountId).first()
        if manager:
            ##---分派從屬關係#多對多中，由TManager來發起新增。
            if smdics:
                #print("SubManager:",len(smdics),type(smdics))
                for m in smdics:
                    accountId=m["username"]
                    mana=TManager.query.filter_by(accountId=accountId).first()
                    if mana:
                        mana.bossID=manager.uid
            
            
            
            ##--分派user的管理者。
            #從tuser原始CSV中，找到跟資料庫manager相匹配的attri, 。再分派關係
            if udics:
                if type(udics)==dict:
                    userid=udics["userid"]
                    user=TUser.query.filter_by(accountId=userid).first()
                    if user:
                        manager.userLIST.append(user)


                elif type(udics)==list:
                    
                    for u in udics:
                        userid=u["userid"]
                        user=TUser.query.filter_by(accountId=userid).first()
                        if user:
                            manager.userLIST.append(user)
                
    db.session.flush()
    db.session.commit()
    return
def connect_relation_user():

    ###---001讀取原始的類別資料以及相關資料的RAW檔, 在此主角是TUser, 關聯的類別為facility, manager(檢查是否有重複), activity---------------
    #mariaDB內會多些TUser是文字檔沒有的。需特別檢查過。
    global foldermj
    #---載入TManager-------
    lines       =get_lines_read(foldermj+"tuserinfo.txt")
    
    managers    =get_lines_read(foldermj+"tmanager.txt")    
    facilitys=get_lines_read(foldermj+"tfacility.txt")
    activitys=get_lines_read(foldermj+"tactivity.txt")
    
    
    managerDic=modify_lines(managers)
    facilityDic=modify_lines(facilitys)
    activityDic=modify_lines(activitys)
    
    #先從RAW檔中找
    for i in range(len(lines)):
        ###---002找到該類別RAW檔中所定義的關聯關係ID，並據此去搜尋該類別在mariaDB內的uid---------------
        dic=json.loads(lines[i])
        accountId=dic["userid"]
        #-------------先找出原始TUser中，紀載跟各類別相關的物件---
        managerIDs                  =detect_none(dic["therapist"],"")
        facilitysIDs                =detect_none(dic["facilityid"],"")#查是否有相關
        activitysIDs                =detect_none(dic["userid"],"")
        
        #--以UserInfo(csv)內的對應數值作為輸入值，到其他類別找到對應該資料的整個類別(實作)
        #例,userinfo有個欄位叫做therapist, 在tmanager內對應的欄位叫做username, 兩邊的值都應該是c.welfuture01--->新的格式中稱為accountId
        #例, userinfo有個欄位叫做facilityid, 在tfacility內有個對應欄位也叫做facilityid, 兩邊有個值314BBC8C76941000002813,新的格式(mariaDB)中是key
        #例,userinfo內有個userid(紀錄mac為主),在tactivity內對應的欄位叫做userid,用該資料的activityid,去對應新的資料格式key
        mdics,mindexs       =query_lines(managerDic,"username",managerIDs)#
        fdics,uindexs       =query_lines(facilityDic,"facilityid", facilitysIDs)
        adics,aindexs       =query_lines(activityDic,"userid", activitysIDs)
        
        #--從資料庫來找
        user=TUser.query.filter_by(accountId=accountId).first()
        
        if user:
            
            if mdics:
                if type(mdics)==dict:
                    accountId=mdics["username"]
                    mana=TManager.query.filter_by(accountId=accountId).first()
                    if mana:
                        user.managerLIST.append(mana)
                elif type(mdics)==list:
                    
                    for m in mdics:

                        accountId=m["username"]
                        mana=TManager.query.filter_by(accountId=accountId).first()
                        if mana:
                            user.managerLIST.append(mana)
            
            ##---分派從屬關係#多對多中，由TManager來發起新增。
            if fdics:
                #print(type(fdics),"Facility:",len(fdics),fdics)
                if type(fdics)==dict:
                    key=fdics["facilityid"]
                    fac=TFacility.query.filter_by(key=key).first()
                    if fac:
                        user.facilityID=fac.uid
                      
                elif type(fdics)==list:
                    for f in fdics:
                        key=f["facilityid"]
                        fac=TFacility.query.filter_by(key=key).first()
                        if fac:
                            user.facilityID=fac.uid
                      
                
            if adics:
                if type(adics)==dict:
                    key=adics["activityid"]
                    act=TActivity.query.filter_by(key=key).first()    
                    if act:
                        user.activityLIST.append(act)
                        
                    
           
    db.session.flush()
    db.session.commit()
    return
def connect_relation_activity():

    ###---001讀取原始的類別資料以及相關資料的RAW檔, 在此主角是TActivity, 從中發現需要建立的關聯為類別為userid, 以及可能的facilityid?---------------
    #mariaDB內會多些TUser是文字檔沒有的。需特別檢查過。
    global foldermj
    print("--loading activity relationships(time consuming)--")
    #---載入TManager-------
    lines       =get_lines_read(foldermj+"tactivity.txt")
    
    users    =get_lines_read(foldermj+"tuserinfo.txt")    
    facilitys=get_lines_read(foldermj+"tfacility.txt")
    
    
    usersDic=modify_lines(users)
    facilityDic=modify_lines(facilitys)
    #activityDic=modify_lines(activitys)
    
    #先從RAW檔中找
    #for i in range(1000,2000):
    
    for i in range(len(lines)):
        if (i%10000)==0:
            print("目前達到",i)
        ###---002找到該類別RAW檔中所定義的關聯關係ID，並據此去搜尋該類別在mariaDB內的uid---------------

        dic=json.loads(lines[i])
        activityId=dic["activityid"]
        #-------------先找出原始TUser中，紀載跟各類別相關的物件---
        userIDs                    =detect_none(dic["userid"],"")
        facilityIDs                =detect_none(dic["facilityid"],"")#查是否有相關
        
        #--以TActivity(csv)內的對應數值作為輸入值，到其他類別找到對應該資料的整個類別(實作)
        #例,tactivity有個欄位叫做userid, 在tuser對應的欄位叫做userid, 目前找不到對應值(有可能在資料庫內有)>新的格式中稱為accountId
        #例,tactivity有個欄位叫做facilityid, 在tfacility內有個對應欄位也叫做facilityid, 兩邊有個值314BBC8C76941000002813,新的格式(mariaDB)中是key
        
        udics,uindexs       =query_lines(usersDic,"userid",userIDs)#
        
        #--從資料庫來找
        activity=TActivity.query.filter_by(key=activityId).first()
        
        if activity:
            if udics:

                if type(udics)==dict:
                    accountId=udics["userid"]
                    user=TUser.query.filter_by(accountId=accountId).first()

                    if user:
                        activity.userID=user.uid
                        
                elif type(udics)==list:
                    
                    for u in udics:

                        accountId=u["userid"]
                        user=TUser.query.filter_by(accountId=accountId).first()
                        if user:
                            activity.userID=user.uid
                            
            ##---分派從屬關係#多對多中，由TManager來發起新增。
            
           
           
            
    db.session.flush()
    db.session.commit()
    return
def connect_relation_event():

    ###---001讀取原始的類別資料以及相關資料的RAW檔, 在此主角是event, 關聯的類別為manager,customer, facility---------------
    lines=get_lines_read(folder+"teventModify.txt")
    customers=get_lines_read(folder+"tcustomerModify.txt")    
    facilitys=get_lines_read(folder+"tfacilityModify.txt")
    
    customerDic=modify_lines(customers)
    facilityDic=modify_lines(facilitys)

    for i in range(len(lines)):
        
        eventuid=i+1
        
    ###---002找到該類別RAW檔中所定義的關聯關係ID，並據此去搜尋該類別在mariaDB內的uid---------------
        dic=json.loads(lines[i])
        managerID       =int(dic["managerID"])
        customerID      =int(dic["customerID"])
        facilityID      =int(dic["facilityID"])
        cdic,cindex=query_lines(customerDic,"id",customerID)
        fdic,findex=query_lines(facilityDic,"id",facilityID)
        print("1.eventUID:",eventuid,",ManagerID:",managerID,",customerID",customerID,"at",cindex,",facilityID",facilityID,"at",findex)        
        mana=None
        cust=None
        faci=None
    ###---003確認RAW檔案中的ID對應的資料目前存在資料庫內---------------
    
        try:
            mana=TManager.query.filter_by(uid=managerID).first()
        except:
            print("2-0manager error")
        try:
            cust=TCustomer.query.filter_by(uid=cindex).first()
            print("2-1Customer:",cust)
        except:
            print("2-1ERRor",cindex)
        try:
            faci=TFacility.query.filter_by(uid=findex).first()
        except:
            print("2-2Error")
        print("2-2Facility:",faci)

        
        event=TEvent.query.filter_by(uid=eventuid).first()
        if event:
    ###---004確認該物件存在mariaDB內才建立關聯關係。---------------
            print("3-1 start adding",event,",managerID:",managerID,",facilityID:",findex,",custID:",cindex)
            ##排除沒有的物件。若加入會因此影響關聯資料庫的建立。
            if mana:
                event.managerID=managerID
            if faci:
                event.facilityID=findex
            if cust:
                event.customerID=cindex
        else:
            print("3-2 event not exist")
        print("4.Before Flush:",event)
    db.session.flush()
    db.session.commit()
    """
    TEvent.query.all()
    for c in the_class:
    """ 
    return
def connect_relation_customer():
    ###---001讀取原始的類別資料以及相關資料的RAW檔, 在此主角是customer, 關聯的類別為facility, managerid---------------
    lines=get_lines_read(folder+"tcustomerModify.txt")
    facilitys=get_lines_read(folder+"tfacilityModify.txt")
    
    facilityDic=modify_lines(facilitys)
    for i in range(len(lines)):
        customeruid=i+1
    ###---002找到該類別RAW檔中所定義的關聯關係ID，並據此去搜尋該類別在mariaDB內的uid---------------
        dic=json.loads(lines[i])
        
        managerID       =int(dic["managerID"])
        print("0Manager:",managerID,",DIC:",dic)
        facilityID      =int(dic["facilityID"])
        fdic,findex=query_lines(facilityDic,"id",facilityID)
        print("1.UID:",customeruid,",ManagerID:",managerID,",facilityID",facilityID,"at",findex)        
        mana=None
        faci=None
    ###---003確認RAW檔案中的ID對應的資料目前存在資料庫內---------------
    
        try:
            mana=TManager.query.filter_by(uid=managerID).first()
        except:
            print("2-0manager error")
        try:
            faci=TFacility.query.filter_by(uid=findex).first()
        except:
            print("2-2Error")
        print("2-2Facility:",faci)

        
        cust=TCustomer.query.filter_by(uid=customeruid).first()
        if cust:
    ###---004確認該物件存在mariaDB內才建立關聯關係。---------------
            ##排除沒有的物件。若加入會因此影響關聯資料庫的建立。
            if mana:
                cust.managerID=managerID
            if faci:
                cust.facilityID=findex
        else:
            print("3-2 event not exist")
        print("4.Before Flush:",cust)
        
    db.session.flush()
    db.session.commit()
def connect_relation_activity_sqlite(filename):
    global foldermj
    #---載入TUser-------
    lines=get_lines_read(foldermj+filename)
    print("活動總數",len(lines))
    dispName=[]
    #for i in range(100):
    
    for i in range(len(lines)):
        result=lines[i].split(";")
        activityid=result[0]
        userid=result[1]
        

        user=TUser.query.filter_by(accountId=userid).first()
        if user:
            if (user.accountId != "NULLUSER") and (user.accountId != "userid"):  
                act=TActivity.query.filter_by(key=activityid).first()
                user.activityLIST.append(act)
            
    db.session.flush()
    db.session.commit()
def backup_relationship():
    ##02建立類別間的關聯，一樣從原始文字檔讀取。
    connect_relation_event()
    connect_relation_customer()
    print("完成CRM資料的讀取")
    connect_relation_facility()
    connect_relation_manager()
    connect_relation_user()
    connect_relation_activity()
    print("從sqlite來的，像是元保宮")
    connect_relation_activity_sqlite("tactivity-yuan.txt")
    return "建立關聯性"
def backup_check():
    print("***backup check!!!")
    try:
    
        sql="select vender from tapifacility"
        result=db.engine.execute(sql)
        print(result)
    except:
        print("指令無笑哈哈")
    
    return "aipFacility與建立device的可能性"
def show_all(the_class):
    for c in the_class:
        print(type(c),"->",c)
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


def mysql_build_facility():
    #元保宮
    facilityList=["803253C72E96","A85E4538610C"]
    for fkey in facilityList:
        f=TFacility.query.filter_by(key=fkey).first()
        if not f:
            newfac=TFacility()
            newfac.key=fkey
            newfac.displayName="中國醫元保宮"
            db.session.add(newfac)
    db.session.commit()
    #--從tapifacility建立facility
    sql="select mac from tapifacility"
    result=db.engine.execute(sql).fetchall()
    
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
def mysql_build_userfacility():
    users=TUser.query.filter(TUser.facilityID.is_(None)).all()
    return str(users)
def backup_check():
    mysql_build_facility()
    mysql_build_userfacility()
    return ""
def rela_test():
    ##00測試self reference的使用方式。
    #map_column, and db.relation
    
    """
    nameList=["陳輝宏","劉啟焉","劉長備","劉恢富","劉快陶","李伯安","劉絞辯","王子安"]
    nameLen=len(nameList)
    index=random.randrange(0,nameLen)
    
    
    #設定
    for i in range(0,nameLen):
        manager=TManager()
        manager.gender=0
        manager.realName=nameList[i]
        db.session.add(manager)
    db.session.commit()
    managers=TManager.query.all()
    count=0
    for p in managers:
        #count=count+1
        p.bossID=2
        db.session.flush()
    db.session.commit()
    managers=TManager.query.all()
    for p in managers:
        print(p.uid,p.realName,"這人:",p.bossID,"=>",p.submanagerLIST)
        print("----")
    db.session.commit()
        
    """
    ##00備份最新資料庫到文字資料中。
    ##01CRM原始類別讀入，並去除不需的變數
    ##02建立類別間的關聯，一樣從原始文字檔讀取。
    ##03依序檢查TEvent-Facility,userID,customerList
    
    #show_all(TManager.query.all())
    
    #show_all(TFacility.query.all())
    #show_all(TEvent.query.all())
    #show_all(TManager.query.all())
    ##04更新使用者的密碼:
    #crm_user_password()
    return "讀一下!"+"done"
