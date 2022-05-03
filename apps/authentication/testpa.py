import pymysql
import requests
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
def update_request_device(data,topic,terminaldate,status):

    for d in data:
        if d["topic"]==topic:
            print(d)
            d["status"]=status
            d["terminaldate"]=terminaldate
            d["action"]="update_facility"
            print(d)
            requests.post(url, data = d)
def autho_device(device_info,topic="HAPPYGOGO",status="LUXURY"):
    nodueday="2060-12-30"
    device_data=get_request_device(device_info)
    update_request_device(device_data,topic,nodueday,status)
def terminate_device(device_info,topic="HAPPYGOGO"):
    terminate="2000-12-30"
    device_data=get_request_device(device_info)
    status="BASIC"
    update_request_device(device_data,topic,terminate,status)
def show_device(device_info):
    device_data=get_request_device(device_info)
    for data in device_data
    
  






















  
    
    :
        print(data)
    print("------------------")
deviceList=["NTTU_PC01","NTTU_PC02","NTTU_PC03","NTTU_PC04","NTTU_PC05","NTTU_PC06","NTTU_PC07","NTTU_PC08","NTTU_PC09","NTTU_PC10","NTTU_PC01","NTTU_PC01","NTTU_PC01","NTTU_PC01","NTTU_PC15"]
show_device("D0C63737CCCE")
auto_device()
