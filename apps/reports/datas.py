from apps.authentication.models import TFacility,TEvent,TManager, TProject, TCustomer
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
    """
    def get_event(self,ownerid):
        
        result=TEvent.query.filter(TEvent.accountId==ownerid,TEvent.type>=0).order_by(TEvent.uid.desc()).all()
        return result
    """
    def get_all_project_number(self):
        return TProject.query.count()
    def get_all_activity_number(self):
        return TEvent.query.count()
        
    def get_facility(self):
        result=TFacility.query.all()
        return result
    def get_customer(self,ownerid):
        #result=TCustomer.query.filter_by(ownerid=ownerid).all()
        result=TCustomer.query.all()
        return result    
    def get_customer_name(self,customeruid):
        try:
            customer=TCustomer.query.filter(TCustomer.uid==customeruid).first()
            if customer:
                name=customer.realName
        except:
            name="乖乖"
      
        return name
    def get_facility_name(self,facilityid):
        name="facility"
        try:
            facility=TFacility.query.filter_by(uid=facilityid).first()
            if facility:
                name=facility.displayName
        except:
            pass

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
        act=TEvent.query.filter_by(uid=activityid).first()
        if act:

            act.type=-99
            act.update()
        
        act=TEvent.query.filter_by(uid=activityid).first()
       
        return
    def write_activitylist(self):
        result=TEvent.query.all()
        
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
    
        result=db.engine.execute("ALTER TABLE TEvent ADD priority Integer")
        result=db.engine.execute("ALTER TABLE TEvent ADD winrate Integer")
        result=db.engine.execute("ALTER TABLE TEvent ADD customerType Integer")
        print("result:",result)
        """
        result=TEvent.query.all()
        print("所有資料:",len(result))
        
        for me in result:
            db.session.delete(me)
        db.session.commit()
        result=TEvent.query.all()
        print("所有資料:",len(result))
        
        return "完成!"
        """
    def string_datetime(self,value,ref):
        result=""
        if value is None:
            value=datetime.now()
        #datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
        result=value.strftime(ref)
        
        return result
    def get_report_general(self,usermanager,form):
        print("----TYPE:",usermanager,usermanager.__tablename__)
        ownerid=usermanager.uid
        #--1先修改---
        if form:
            print("0預備更新")
        
            event=TEvent.query.filter_by(uid=form.activityid).first()
            if event:
                event.description=form.description
                event.nextStep=form.nextstep  
                event.update()

               
            else:
                print("找不到可惡!")
        #--2抓值----
        events=usermanager.eventLIST
        
        fac=self.get_facility()
        cust=usermanager.customerLIST
        count=0
        events=list(reversed(events))
        for a in events:
            type      =a.type
            customer_name=self.get_customer_name(a.customerID)
            facility_name=self.get_facility_name(a.facilityID)

            events[count].displayStartTime=self.string_datetime(a.startTime,"%H:%M")
            events[count].displayEndTime=self.string_datetime(a.endTime,"%H:%M")
            events[count].displayStartDate=self.string_datetime(a.startTime,"%m-%d")
            events[count].displayNextDate=self.string_datetime(a.nextTime,"%m-%d")            
            events[count].customer=customer_name
            events[count].facility=facility_name
            events[count].strtype=self.get_type_str(a.type)
            events[count].strpriority=self.get_priority_str(a.priority)
            events[count].strwinrate=self.get_priority_str(a.winrate)
            count=count+1
        
        print("#---統計資料--------------------")
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
        print("render----")
        return render_template('report/report_general.html',static=static,activity=events,facility=fac,customer=cust,usermanager=usermanager)
    #001產出每周的報表
    def cal_facility_sorted_act(self,events):
            #--設定順序，並修改原有的events-----------
        facdic={}
        for main in events:
            fac_customer=str(main.facilityID).zfill(10)+str(main.customerID).zfill(10)
            if fac_customer not in facdic:
                target_facility=fac_customer
                latest_date=datetime(1979,1,13)
                for a in events:
                    a_fac_customer=str(a.facilityID).zfill(10)+str(a.customerID).zfill(10)
                    #print("新組合成:",a_fac_customer)
                    if a_fac_customer == target_facility:
                        #print((a.nextTime>latest_date),"**",a.nextTime,"-->",latest_date)
                        if a.nextTime>latest_date:
                            latest_date=a.nextTime
                facdic[fac_customer]=latest_date
                
        
        faclist=sorted(facdic.items(), key=lambda x:x[1])
        facdic={}
        for f in faclist:
            facdic[f[0]]=f[1]

        new_act=[]
        #-修改events所有活動的順序了
        for key, value in facdic.items():
            for a in events:
                a_fac_customer=str(a.facilityID).zfill(10)+str(a.customerID).zfill(10)
                if a_fac_customer == key:
                    new_act.append(a)
                    
        return new_act
    #002調整的報表
    from datetime import datetime
    def cal_modify_act(self,events):
        count=0

        customerLIST=[]
        facilityLIST=[]
        for a in events:
            #customer_name=self.get_customer_name(a.customerID)
            #facility_name=self.get_facility_name(a.facilityID)
            customerLIST.append(a.customerID)
            facilityLIST.append(a.facilityID)
            events[count].customer=""
            events[count].facility=""
            events[count].strtype=self.get_type_str(a.type)
            events[count].description=events[count].description.replace("\n","<br>")
            events[count].nextStep=events[count].nextStep.replace("\n","<br>")
            count=count+1
        customerLIST=set(customerLIST)
        facilityLIST=set(facilityLIST)
        customers=TCustomer.query.filter(TCustomer.uid.in_(customerLIST)).all()
        facilitys=TFacility.query.filter(TFacility.uid.in_(facilityLIST)).all()
        print("customer:",customerLIST)
        print("facility:",facilityLIST)
        customerDIC={}
        facilityDIC={}
        facilityDIC["ray"]="好帥"
        for f in facilitys:
            facilityDIC[str(f.uid)]=f.displayName
        for c in customers:
            customerDIC[str(c.uid)]=c.realName

        count=0
        for a in events:
            if events[count]:
                if a.customerID:
                    events[count].customer=customerDIC[str(a.customerID)]
                if a.facilityID:
                    events[count].facility=facilityDIC[str(a.facilityID)]
                
                    
            count=count+1

        return events
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

    def cal_modify_facility(self,events):
        facility=[]
        result_facility=[]
        for main in events:
            main_facust=str(main.facilityID).zfill(10)+str(main.customerID).zfill(10)
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
                for a in events:
                    #相同的機構
                    customerid=a.customerID
                    
                    a_facust=str(a.facilityID).zfill(10)+str(customerid).zfill(10)
                    if main_facust == a_facust:
                        
                        customer.append(a.customer)
                        

                        
                        time_string="-"
                        try:
                            
                            if a.startTime is not None:
                                time_string=str(a.startTime).split(" ")[0]
  
                        except:
                            pass
                        
                        next_step_str="-"
                        try:
                            if a.nextStep is not None:
                                next_step_str=a.nextStep
                        except:
                            pass
                            
                        description_str="-"
                        try:
                            if a.description is not None:
                                description_str=a.description
                        except:
                            pass
                        strtype_str="-"
                        try:
                            if a.strtype is not None:
                                strtype_str=a.strtype
                        except:
                            pass
                        customer_str="-"
                        try:
                            if a.customer is not None:
                                customer_str=a.customer
                        except:
                            pass
                        fac["customer"]=fac["customer"]+"<strong>"+time_string+":"+strtype_str+customer_str+"</strong><br>"+description_str+"<br><u>下一步</u><br>"+next_step_str+"<br>"
                        fac["facilityid"]=main.facilityID
                        fac["customerid"]=main.customerID
                        fac["activityid"]=main.uid
                        fac["type"]=main.type
                        fac["priority"]=self.get_priority_str(a.priority)
                        fac["winrate"]=self.get_priority_str(a.winrate)
                        fac["customerType"]=0
                        if a.nextTime>passdate:
                            passdate=a.nextTime

                        
                        
                        
                        customerN=customerN+1
                namestring="{0}優先,{1}勝率,{2}-{3}".format(fac["priority"],fac["winrate"],fac["name"],fac["customer_name"])
                fac["name"]=namestring
                if passdate<=now:
                    fac["name"]=fac["name"]+"<font color=\"red\">過期日:"+passdate.strftime("%m-%d")+"</font>"
                else:
                    fac["name"]=fac["name"]+"追蹤日:"+passdate.strftime("%m-%d")
                result_facility.append(fac)
                
                
        

        
        return result_facility
    def cal_report_facility_user(self,usermanager):
    
        print("cal_report_facility_user:",usermanager)
        print("ID:",usermanager.uid)
        ownerid=usermanager.uid
        events=usermanager.eventLIST#   self.get_event(ownerid)
        
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
        print("--ACT總數:",len(events))
        
        #-----------依照時間來排序各機構的順序(之後應該是機構+使用者名稱)---------
        events=self.cal_facility_sorted_act(events)

        
        #----------修訂相關-------------------
        events=self.cal_modify_act(events)
        print("--修訂相關後的ACT:",len(events))
        #-----------------------------彙整
        result_facility=self.cal_modify_facility(events)
        print("--彙整後的機構數::",len(result_facility))
        return result_facility    
    def cal_report_weekly(self,usermanager):
        events=usermanager.eventLIST
        count=0
        start_day,end_day=self.get_duration_edge()
        print("Start:",start_day)
        print("End:",end_day)

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
        #--設定順序，並修改原有的events-----------
        facdic={}
        for main in events:
            if main.facilityID not in facdic:
                target_facility=main.facilityID
                latest_date=datetime(1979,1,13)
                for a in events:
                    if a.facilityID == target_facility:
                        if a.nextTime>latest_date:
                            latest_date=a.nextTime
                facdic[main.facilityID]=latest_date
                
        faclist=sorted(facdic.items(), key=lambda x:x[1])
        facdic={}
        for f in faclist:
            facdic[f[0]]=f[1]
        new_act=[]
        #-修改events所有活動的順序了
        for key, value in facdic.items():
            for a in events:
                if a.facilityID == key:
                    new_act.append(a)
                    
        events=new_act
        
        
        
        #----------修訂相關-------------------
        for a in events:
            customerid=a.customerID
            facilityid=a.facilityID
            type      =a.type
            customer_name=self.get_customer_name(customerid)
            
            
            facility_name=self.get_facility_name(facilityid)
            events[count].customerID=customerid
            events[count].customer=customer_name
            events[count].facility=facility_name
            events[count].strtype=self.get_type_str(a.type)
            events[count].description=events[count].description.replace("\n","<br>")
            events[count].nextStep=events[count].nextStep.replace("\n","<br>")
            count=count+1
        
        #-----------------------------彙整
        facility=[]
        result_facility=[]
        for main in events:
            if main.facilityID not in facility:
                fac=dict()
                facility.append(main.facilityID)
                fac["name"]=main.facility

                customer=[]
                fac["customer"]=""
                fac["customer_name"]=main.customer
                customerN=0
                
                
                
                passdate=datetime(2013,1,13)
                now=datetime.now()
                for a in events:
                    #相同的機構
                    if main.facilityID == a.facilityID:
                        
                        customer.append(a.customer)
                        fac["customer"]=fac["customer"]+"<strong>"+str(a.startTime).split(" ")[0]+":"+a.strtype+a.customer+"</strong><br>"+a.description+"<br><u>下一步</u><br>"+a.nextStep+"<br>"
                        fac["facilityid"]=main.facilityID
                        fac["customerid"]=main.customerID
                        fac["activityid"]=main.uid
                        fac["type"]=main.type

                        if a.nextTime>passdate:
                            passdate=a.nextTime
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
        result=TEvent.query.filter(TEvent.type <=0).all()
        
        for r in result:
            r.type=0
            r.update()
            