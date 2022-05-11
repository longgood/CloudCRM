
import requests

from datetime import datetime
# 資料庫設定
url = "http://api.longgood.com.tw/script/unitycertify.php"

def connect_mysql():
    try:
        # 建立Connection物件
        conn = pymysql.connect(**db_settings)
        # 建立Cursor物件
        with conn.cursor() as cursor:
            # 查詢資料SQL語法
            command = "SELECT * FROM TFacility"
            # 執行指令
            cursor.execute(command)
            # 取得所有資料
            result = cursor.fetchall()
            print(result)
        
          #資料表相關操作
    except Exception as ex:
        print(ex)
def analysis_string(str_result):
    items=str_result.split("<br>")
    result=[]
    for item in items:
        data=item.split(",")
        
        if(data and len(data)>1):
            info={}
            info["topic"]=data[0]
            info["status"]=data[1]
            info["mac"]=data[2]
            info["logintime"]=data[3]
            info["terminaldate"]=data[4]
            if (len(data) > 5):info["vender"] = data[5]
            if (len(data) > 6):info["name"] = data[6]
            result.append(info)
    return result
def get_request_device(device_name):

    myobj = {"action":"query_facility","name":device_name}
    
    x = requests.post(url, data = myobj)
    return analysis_string(x.text)
    
def get_latest(infos):
    target_info={}
    index=0
    now=datetime.now()
    history=datetime(1979, 4, 18)
    maxdate=now-history
    for info in infos:
        date=datetime.strptime(info["logintime"],"%Y-%m-%d %H:%M:%S")
        delta=now-date
        if delta<maxdate:
            maxdate=delta
            target_info=info
    return target_info
def update_request_device(data,topic,terminaldate,status):
    infos=[]
    for d in data:
        if d["topic"]==topic:
            d["status"]=status
            d["terminaldate"]=terminaldate
            d["action"]="update_facility"
            infos.append(d)
    target=get_latest(infos)
    if target:
        x=requests.post(url, data = target)
        print("這在邊進行更新",x.text,"->",target)
        
    return target
def autho_device(device_info,topic="HAPPYGOGO",nodueday="2060-12-30",status="LUXURY"):
    device_data=get_request_device(device_info)
    return update_request_device(device_data,topic,nodueday,status)
def terminate_device(device_info,topic="HAPPYGOGO"):
    terminate="2000-12-30"
    device_data=get_request_device(device_info)
    status="BASIC"
    update_request_device(device_data,topic,terminate,status)
def show_device(device_info):
    device_data=get_request_device(device_info)
    for data in device_data:
        print(data)
    return device_data
    
def task_001():
    deviceList=[""]
    deviceinfo="D0C63737CCCE"
    show_device(deviceinfo)
    autho_device(deviceinfo,"GAITBEST","2022-04-30")
    autho_device(deviceinfo,"MAJESTY","2022-04-30")
    terminate_device(deviceinfo,"HAPPYGOGO")
    show_device(deviceinfo)
def task_nttu():

    #devicelist=["NTTU_PC01","NTTU_PC02","NTTU_PC03","NTTU_PC04","NTTU_PC05","NTTU_PC06","NTTU_PC07","NTTU_PC08","NTTU_PC09","NTTU_PC10","NTTU_PC11","NTTU_PC12","NTTU_PC13","NTTU_PC14","NTTU_PC15"]
    devicelist=["3C9C0FE449F9", "F8A2D66219FB", "F8A2D65C598D", "70C94ED279D3", "F8A2D66234D1", "F8A2D65821BF", "F8A2D66234BF", "F8A2D65C652B", "C0B8837CCBEE", "38DEAD24FEDC", "DCFB489D60F2", "5C879C2AAB07", "F8A2D6623F81", "F8A2D6581BFF", "04D9F50F9C3E"]
    for device in devicelist:
        result=show_device(device)
    isGo=True
    if isGo:
        print("開始設定:")
        nList=[]
        for device in devicelist:
            result=autho_device(device)
            if not result:
                nList.append(device)
        print("尚未開機或是上網開通:",nList)   
def terminate_nttu():
    devicelist=["NTTU_PC01","NTTU_PC02","NTTU_PC03","NTTU_PC04","NTTU_PC05","NTTU_PC06","NTTU_PC07","NTTU_PC08","NTTU_PC09","NTTU_PC10","NTTU_PC11","NTTU_PC12","NTTU_PC13","NTTU_PC14","NTTU_PC15"]
    for device in devicelist:
        result=show_device(device)
    isGo=True
    if isGo:
        print("開始設定:")
        nList=[]
        for device in devicelist:
            result=terminate_device(device)
            if not result:
                nList.append(device)
        print("尚未開機或是上網開通:",nList)   
def go_backupdb():
    sql="SELECT * FROM 'TFacility' WHERE 1"
    myobj = {"action":"set_facility","sql":sql}
    
    x = requests.post(url, data = myobj)
    print(x.text)
#task_nttu()
def go_backup_query():

    wordList=["LongGood","龍骨王","NullVender","New","Furoto","Kerry"]
    facilityList=[]
    for word in wordList:
        result=get_request_device(word)
        print(word)
        for r in result:
            facilityList.append(r)
    unique_facility=[]
    unique_mac=[]
    print("raw:",len(facilityList))
    for facility in facilityList:
        if facility["mac"] not in unique_mac:
            unique_facility.append(facility)
            unique_mac.append(facility["mac"])
    print("trim:",len(unique_facility))    
    for f in unique_facility:
        print(f)
def group_authorize(devicelist,isGo=False,topic="HAPPYGOGO",nodueday="2060-12-30",status="LUXURY"):
        
    for device in devicelist:
        result=show_device(device)
   
    if isGo:
        print("開始設定:")
        nList=[]
        for device in devicelist:
            result=autho_device(device,topic,nodueday,status)
            if not result:
                nList.append(device)
        print("尚未開機或是上網開通:",nList) 
def nttu_setting():
    print("這是20220510台東遠距復健計畫新增開通")
    devicelist=["parayapay","Pungudang01","kaadaadaan","mingatw","LC01","Tamalrakaw","TAIBEN","maysa","lp01","Aljungic"]
    group_authorize(devicelist,True,topic="HAPPYGOGO",nodueday="2022-11-07")
nttu_setting()        
#autho_device("DC8B280D7A8C","MAJESTY",nodueday="2060-12-30",status="LUXURY")
#go_backupdb()