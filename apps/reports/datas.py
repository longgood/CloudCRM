from apps.authentication.models import TFacility,TVisiting,TCustomer, TProject
from flask import render_template
from flask_babel import *
from collections import OrderedDict
from datetime import datetime,timedelta
from werkzeug.datastructures import ImmutableMultiDict
import json
from apps import db
#所有資料的介面

def ActivityToDict(act):
    dic=act.get_dic()

    return dic
class TData():
    usermanager="操作(使用)者名稱"
    current_patientid="病人姓名"
    def __init__(self):
        return
    def get_activity(self,ownerid):
        result=TVisiting.query.filter(TVisiting.ownerid==ownerid,TVisiting.type>=0).order_by(TVisiting.id.desc()).all()
        
        return result
    def get_all_project_number(self):
        return TProject.query.count()
    def get_all_activity_number(self):
        return TVisiting.query.count()
        
    def get_facility(self):
        result=TFacility.query.all()
        return result
    def get_customer(self,ownerid):
        result=TCustomer.query.filter_by(ownerid=ownerid).all()
        return result    
    def get_customer_name(self,customerid):
        name=TCustomer.query.filter_by(id=customerid).first().name
        
        return name
    def get_facility_name(self,facilityid):
        name=TFacility.query.filter_by(id=facilityid).first().name
        return name
    def get_type_str(self,type):
        result="隨意!"
        if type==0:
            result="寫信"
        elif type==1:
            result="LINE"
        elif type==2:
            result="線上通話"
        elif type==3:
            result="會面"
        elif type==4:
            result="面對面三人以上會議"
    
        return result
    def get_priority_str(self,input):
        
        result="一般"
        if input==50:
            result="一般"
        elif input==25:
            result="低"
        elif input==75:
            result="高"
        elif input==100:
            result="極高"
        elif input==0:
            result="極低"
    
        return result
    def hide_activity(self,activityid):
        act=TVisiting.query.filter_by(id=activityid).first()
        if act:

            act.type=-99
            act.update()
        
        act=TVisiting.query.filter_by(id=activityid).first()
       
        return
    def write_activitylist(self):
        result=TVisiting.query.all()
        
        result=json.dumps(result, default=ActivityToDict,ensure_ascii=False)
        
        path = 'd://actbackup.json'
        with open(path, 'w',encoding='UTF-8') as f:
            f.write(result)
    def read_activitylist(self):
        path = 'd://actbackup.json'
        
        with open(path, 'r',encoding='UTF-8') as f:
            result=json.load(f)
        for r in result:
            print("actlist:",r)
        print("資料長度:",len(result))
        
    def reports_activity_update(self):
    
        result=db.engine.execute("ALTER TABLE TVisiting ADD priority Integer")
        result=db.engine.execute("ALTER TABLE TVisiting ADD winrate Integer")
        result=db.engine.execute("ALTER TABLE TVisiting ADD customerType Integer")
        print("result:",result)
        """
        result=TVisiting.query.all()
        print("所有資料:",len(result))
        
        for me in result:
            db.session.delete(me)
        db.session.commit()
        result=TVisiting.query.all()
        print("所有資料:",len(result))
        
        return "完成!"
        """
    def get_report_general(self,usermanager,form):
        ownerid=usermanager.id
        #--1先修改---
        if form:
            print("0預備更新")
        
            act=TVisiting.query.filter_by(id=form.activityid).first()
            if act:
                print("1.準備更新")

                act.description=form.description
                act.nextstep=form.nextstep  
                act.commit_update()
                print("已經更新")
        
        #--2抓值----
        
        acts=self.get_activity(ownerid)
        fac=self.get_facility()
        cust=self.get_customer(ownerid)
        count=0
        for a in acts:
            customerid=a.customerList.split(";")[0]
            facilityid=a.facilityid
            type      =a.type
            customer_name=self.get_customer_name(customerid)
            facility_name=self.get_facility_name(facilityid)
            acts[count].customer=customer_name
            acts[count].facility=facility_name
            acts[count].strtype=self.get_type_str(a.type)
            acts[count].priority=self.get_priority_str(a.priority)
            acts[count].winrate=self.get_priority_str(a.winrate)
            count=count+1
            
        #---統計資料--------------------
        all_project_number=self.get_all_project_number()
        print("=======",all_project_number)
        all_activity_number=self.get_all_activity_number()
        my_activity_number=count
        static={}
        static["all_act_num"]=all_activity_number
        static["my_act_num"]=my_activity_number
        static["title_all_act_num"]=gettext("title_all_act_num")
        static["title_my_act_num"]=gettext("title_my_act_num")
        return render_template('report/report_general.html',static=static,activity=acts,facility=fac,customer=cust,usermanager=usermanager)
    #001產出每周的報表
    def cal_facility_sorted_act(self,acts):
            #--設定順序，並修改原有的acts-----------
        facdic={}
        for main in acts:
            fac_customer=main.facilityid+main.customerList.split(";")[0]
            if fac_customer not in facdic:
                target_facility=fac_customer
                latest_date=datetime(1979,1,13)
                for a in acts:
                    a_fac_customer=a.facilityid+a.customerList.split(";")[0]
            
                    if a_fac_customer == target_facility:
                        if a.nexttime>latest_date:
                            latest_date=a.nexttime
                facdic[fac_customer]=latest_date
                
        faclist=sorted(facdic.items(), key=lambda x:x[1])
        facdic={}
        for f in faclist:
            facdic[f[0]]=f[1]
        new_act=[]
        #-修改acts所有活動的順序了
        for key, value in facdic.items():
            for a in acts:
                a_fac_customer=a.facilityid+a.customerList.split(";")[0]
                if a_fac_customer == key:
                    new_act.append(a)
                    
        return new_act
    #002調整的報表
    def cal_modify_act(self,acts):
        count=0
        for a in acts:
            customerid=a.customerList.split(";")[0]
            facilityid=a.facilityid
            type      =a.type
            customer_name=self.get_customer_name(customerid)
            
            
            facility_name=self.get_facility_name(facilityid)
            acts[count].customerid=customerid
            acts[count].customer=customer_name
            acts[count].facility=facility_name
            acts[count].strtype=self.get_type_str(a.type)
            acts[count].description=acts[count].description.replace("\n","<br>")
            acts[count].nextstep=acts[count].nextstep.replace("\n","<br>")
            count=count+1
        return acts
    #003調整機構資訊內容    
    def get_priority(self,input):
    
        result=50
        if input=="一般":
            result=50
        elif input=="高":
            result=75
        elif input=="低":
            result=25
        elif input=="超低":
            result=0
        elif input=="超高":
            result=100
        return result

    def cal_modify_facility(self,acts):
        facility=[]
        result_facility=[]
        for main in acts:
            main_facust=main.facilityid+main.customerList.split(";")[0]
            #取代facilityid
            
            if main_facust not in facility:
                fac=dict()
                facility.append(main_facust)
                fac["name"]=main.facility

                customer=[]
                fac["customer"]=""
                fac["customer_name"]=main.customer
                customerN=0
                
                
                
                passdate=datetime(2013,1,13)
                now=datetime.now()
                for a in acts:
                    #相同的機構
                    a_facust=a.facilityid+a.customerList.split(";")[0]
                    if main_facust == a_facust:
                        
                        customer.append(a.customer)
                        fac["customer"]=fac["customer"]+"<strong>"+str(a.starttime).split(" ")[0]+":"+a.strtype+a.customer+"</strong><br>"+a.description+"<br><u>下一步</u><br>"+a.nextstep+"<br>"
                        fac["facilityid"]=main.facilityid
                        fac["customerid"]=main.customerList
                        fac["activityid"]=main.id
                        fac["type"]=main.type
                        fac["priority"]=self.get_priority_str(a.priority)
                        fac["winrate"]=self.get_priority_str(a.winrate)
                        fac["customerType"]=main.customerType
                        

                        if a.nexttime>passdate:
                            passdate=a.nexttime

                        
                        
                        
                        customerN=customerN+1
                        
                fac["name"]=fac["priority"]+"優先,"+fac["winrate"]+"勝率"+fac["name"]+"-"+fac["customer_name"]        
                if passdate<=now:
                    fac["name"]=fac["name"]+"<font color=\"red\">過期日:"+passdate.strftime("%m-%d")+"</font>"
                else:
                    fac["name"]=fac["name"]+"追蹤日:"+passdate.strftime("%m-%d")
                result_facility.append(fac)
        return result_facility
    def cal_report_facility_user(self,usermanager):
        ownerid=usermanager.id
        acts=self.get_activity(ownerid)

        
        start_day,end_day=self.get_duration_edge()
        

        #--需要設定時間-----------
        
        """
        new_act=[]
        for a in acts:
            
            day_diff=(a.starttime.day-start_day)
            tmpday=(a.starttime-timedelta(days=start_day))
            print(tmpday,"day diff:",day_diff,",startday:",start_day)
            if day_diff>=-1:
                print("IN:",a.starttime)
                new_act.append(a)
            else:
                print("Out:",a.starttime)
        #acts=new_act #先不做時間限制
        """
        #-----------依照時間來排序各機構的順序(之後應該是機構+使用者名稱)---------
        acts=self.cal_facility_sorted_act(acts)
        #----------修訂相關-------------------
        acts=self.cal_modify_act(acts)
        
        #-----------------------------彙整
        result_facility=self.cal_modify_facility(acts)
        return result_facility    
    def cal_report_weekly(self,usermanager):
        ownerid=usermanager.id
        acts=self.get_activity(ownerid)
        count=0
        
        start_day,end_day=self.get_duration_edge()
        

        #--需要設定時間-----------
        
        """
        new_act=[]
        for a in acts:
            
            day_diff=(a.starttime.day-start_day)
            tmpday=(a.starttime-timedelta(days=start_day))
            print(tmpday,"day diff:",day_diff,",startday:",start_day)
            if day_diff>=-1:
                print("IN:",a.starttime)
                new_act.append(a)
            else:
                print("Out:",a.starttime)
        #acts=new_act #先不做時間限制
        """
        #--設定順序，並修改原有的acts-----------
        facdic={}
        for main in acts:
            if main.facilityid not in facdic:
                target_facility=main.facilityid
                latest_date=datetime(1979,1,13)
                for a in acts:
                    if a.facilityid == target_facility:
                        if a.nexttime>latest_date:
                            latest_date=a.nexttime
                facdic[main.facilityid]=latest_date
                
        faclist=sorted(facdic.items(), key=lambda x:x[1])
        facdic={}
        for f in faclist:
            facdic[f[0]]=f[1]
        new_act=[]
        #-修改acts所有活動的順序了
        for key, value in facdic.items():
            for a in acts:
                if a.facilityid == key:
                    new_act.append(a)
                    
        acts=new_act
        
        
        
        #----------修訂相關-------------------
        for a in acts:
            customerid=a.customerList.split(";")[0]
            facilityid=a.facilityid
            type      =a.type
            customer_name=self.get_customer_name(customerid)
            
            
            facility_name=self.get_facility_name(facilityid)
            acts[count].customerid=customerid
            acts[count].customer=customer_name
            acts[count].facility=facility_name
            acts[count].strtype=self.get_type_str(a.type)
            acts[count].description=acts[count].description.replace("\n","<br>")
            acts[count].nextstep=acts[count].nextstep.replace("\n","<br>")
            count=count+1
        
        #-----------------------------彙整
        facility=[]
        result_facility=[]
        for main in acts:
            if main.facilityid not in facility:
                fac=dict()
                facility.append(main.facilityid)
                fac["name"]=main.facility

                customer=[]
                fac["customer"]=""
                fac["customer_name"]=main.customer
                customerN=0
                
                
                
                passdate=datetime(2013,1,13)
                now=datetime.now()
                for a in acts:
                    #相同的機構
                    if main.facilityid == a.facilityid:
                        
                        customer.append(a.customer)
                        fac["customer"]=fac["customer"]+"<strong>"+str(a.starttime).split(" ")[0]+":"+a.strtype+a.customer+"</strong><br>"+a.description+"<br><u>下一步</u><br>"+a.nextstep+"<br>"
                        fac["facilityid"]=main.facilityid
                        fac["customerid"]=main.customerList
                        fac["activityid"]=main.id
                        fac["type"]=main.type

                        if a.nexttime>passdate:
                            passdate=a.nexttime
                            print("passdate 2:",passdate)
                        
                        
                        
                        customerN=customerN+1
                        
                        
                if passdate<=now:
                    fac["name"]=fac["name"]+"<font color=\"red\">過期日:"+passdate.strftime("%m-%d")+"</font>"
                else:
                    fac["name"]=fac["name"]+"追蹤日:"+passdate.strftime("%m-%d")
                result_facility.append(fac)
        return result_facility
    def get_report_weekly(self, usermanager):
        result_facility=self.cal_report_weekly(usermanager)
        return render_template('report/report_weekly.html',activity=result_facility)
    #取得期間的前後日期，現在已周為單位，之後再取得月。
    #結果取到的值是絕對的日th, 不是差異。寫錯了。
    def get_duration_edge(self,duration="weekly"):
        now=datetime.now()
        last_start=now-timedelta(days=now.weekday()+7)
        last_end=now-timedelta(days=now.weekday()+1)
        this_start=now-timedelta(days=now.weekday())
        this_end=now-timedelta(days=now.weekday()-6)
        cum_days=(now-this_start).days
        
        if cum_days<3:

            start_day=last_start.day
            end_day=last_end.day
        else:
            start_day=this_start
            end_day=now
        return start_day, end_day
    
    
    def report_recovery(self):
        result=TVisiting.query.filter(TVisiting.type <=0).all()
        
        for r in result:
            r.type=0
            r.update()
            