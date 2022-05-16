from apps.authentication.models import TFacility,TActivity,TCustomer
from apps import db
#from apps.reports.BIOANALYSIS import ClassIADL
from flask import render_template
from collections import OrderedDict
from datetime import datetime, timedelta
#所有資料的介面
class TData():
    usermanager="操作(使用)者名稱"
    current_patientid="病人姓名"
    def __init__(self):
        return
    def get_activity(self,ownerid):
        result=TActivity.query.filter_by(ownerid=ownerid).all()
        return result
    def get_all_activity_number(self):
        return TActivity.query.count()
        
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
    def get_report_general(self,usermanager):
        ownerid=usermanager.id
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
            count=count+1
            
        #---統計資料--------------------
        all_activity_number=self.get_all_activity_number()
        my_activity_number=count
        static={}
        static["all_act_num"]=all_activity_number
        static["my_act_num"]=my_activity_number
        print(static)
        return render_template('report/report_general.html',static=static,activity=acts,facility=fac,customer=cust,usermanager=usermanager)
    #產出每周的報表

    def get_report_weekly(self, usermanager):

        ownerid=usermanager.id
        acts=self.get_activity(ownerid)
        count=0
        
        start_day,end_day=self.get_duration_edge()
        
        #--需要設定時間-----------
        new_act=[]
        for a in acts:
            
            day_diff=(a.starttime.day-start_day)
            if day_diff>=-1:
                print("IN:",a.starttime)
                new_act.append(a)
            else:
                print("Out:",a.starttime)
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
                customerN=0
                for a in acts:
                    #相同的機構
                    if main.facilityid == a.facilityid:
                        #if a.facility is "龍骨王股份有限公司":
                        customer.append(a.customer)
                        fac["customer"]=fac["customer"]+"<strong>"+str(a.starttime).split(" ")[0]+":"+a.strtype+a.customer+"</strong><br>"+a.description+"<br><u>下一步</u><br>"+a.nextstep+"<br>"
                        customerN=customerN+1
                            
                result_facility.append(fac)
        
       
            
        return render_template('report/report_weekly.html',activity=result_facility)
    #取得期間的前後日期，現在已周為單位，之後再取得月。
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
"""
    def __init__(self):
        self.current_patientid="50E085F6B468000001"
        self.iadl=ClassIADL.ClassIADL(True)
        self.iadl.get_test()
        return
    def get_history_activity(self,patientid):
        self.set_current_patientid(patientid)
        DurationData,MeanDurationData,ScoreData,ResponseData,NumData,DayDicDuration,DayDicScore, DayDicResponse,dateList,tableInfo,tableProgress=self.iadl.get_history_activity(self.get_current_patientid())
        return render_template('home/report_history_iadl.html',
                                              user=self.usermanager,
                                              patientList=self.get_patient_list(),
                                              patientInfos=self.iadl.get_userinfo(patientid),
                                              program_table=self.iadl.get_activity_table(),
                                              SingleDurationData=DurationData,
                                              SingleMeanDurationData=MeanDurationData,
                                              SingleScoreData=ScoreData,
                                              SingleResponseData=ResponseData,
                                              SingleNumData=NumData,
                                              SingleDicDurationData=DayDicDuration,
                                              SingleDicScoreData=DayDicScore,
                                              SingleDicResponseData=DayDicResponse,
                                              DateData=dateList,
                                              SingleTableInfoData=tableInfo,
                                              SingleTableProgressData=tableProgress   
                                              )
    def get_single_activity(self,patientid):
        print("data----")
        self.iadl.get_test()
        self.set_current_patientid(patientid)
        
        DurationData,MeanDurationData,ScoreData,NumData,dicDuration,dicScore,tableInfo=self.iadl.get_single_activity(self.get_current_patientid())
        #DurationData,MeanDurationData,ScoreData,NumData,dicDuration,dicScore,tableInfo=ClassIADL.get_single_activity(self.get_current_patientid())
        return render_template('home/report_single_iadl.html',
                        user=self.usermanager,
                        patientList=self.get_patient_list(),
                        patientInfos=self.iadl.get_userinfo(patientid),
                        program_table=self.iadl.get_activity_table(),
                        SingleDurationData=DurationData,
                        SingleMeanDurationData=MeanDurationData,
                        SingleScoreData=ScoreData,
                        SingleNumData=NumData,
                        SingleDicDurationData=dicDuration,
                        SingleDicScoreData=dicScore,
                        SingleTableInfoData=tableInfo
                        )
    def get_activity_table(self):
        return ClassIADL.get_activity_table()
    def get_patient_list(self,prefix="report_single?patientid="):
        return [{"name":"石孟哲","id":prefix+"50E085F6B468000001"},{"name":"小魚","id":prefix+"50E085F6B468000002"},{"name":"王隆谷","id":prefix+"50E085F6B468000003"}]
    def set_current_patientid(self,patientid):
        if patientid is None:
            if self.current_patientid is None:
                patientid="50E085F6B468000001"
            else:
                patientid=self.current_patientid
        self.current_patientid=patientid
        return
    def get_current_patientid(self):
        return self.current_patientid
    def get_patient_info(self):
        patient01="{\"images\":null,\"_labels\":null,\"_values\":null,\"userid\":\"50E085F6B468000001\",\"patientid\":null,\"realname\":\"石孟哲\",\"nationalid\":\"G120164394\",\"birthday\":\"1990/09/20\",\"disease\":null,\"trainingmode\":null,\"height\":179,\"weight\":60,\"gender\":\"Male\",\"phone\":null,\"facilityid\":null,\"therapist\":null,\"status\":0,\"deviceid\":null,\"duration\":null,\"note\":null,\"registertime\":\"2020/11/26 下午 05:10:33\"}"
        patient02="{\"images\":null,\"_labels\":null,\"_values\":null,\"userid\":\"50E085F6B468000002\",\"patientid\":null,\"realname\":\"小魚\",\"nationalid\":\"B220164394\",\"birthday\":\"1994/08/07\",\"disease\":null,\"trainingmode\":null,\"height\":164,\"weight\":39,\"gender\":\"Femal\",\"phone\":null,\"facilityid\":null,\"therapist\":null,\"status\":0,\"deviceid\":null,\"duration\":null,\"note\":null,\"registertime\":\"2020/11/26 下午 05:10:33\"}"
        patient03="{\"images\":null,\"_labels\":null,\"_values\":null,\"userid\":\"50E085F6B468000003\",\"patientid\":null,\"realname\":\"王隆谷\",\"nationalid\":\"G120164394\",\"birthday\":\"1979/08/07\",\"disease\":null,\"trainingmode\":null,\"height\":184,\"weight\":89,\"gender\":\"Male\",\"phone\":null,\"facilityid\":null,\"therapist\":null,\"status\":0,\"deviceid\":null,\"duration\":null,\"note\":null,\"registertime\":\"2022/11/26 下午 05:10:33\"}"
        if self.current_patientid=="50E085F6B468000001":
            return self.iadl.get_userinfo(patient01) 
        elif self.current_patientid=="50E085F6B468000002":
            return self.iadl.get_userinfo(patient02)
        elif self.current_patientid=="50E085F6B468000003":
            return self.iadl.get_userinfo(patient03)
        else:
            return self.iadl.get_userinfo(patient01)
"""
