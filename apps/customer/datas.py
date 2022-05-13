from apps.authentication.models import TFacility,TActivity,TCustomer
from apps import db
from flask import render_template
from datetime import datetime,timedelta
import random
#所有資料的介面
class TCustomerData():
    usermanager="操作(使用)者名稱"
    current_patientid="病人姓名"
    
    def get_id(self,num):
        pre=random.randint(10,99)
        id=pre+num*100+1000000000
        return id
    def get_type(self,input):
        result=0
        if input=="寫信":
            result=0
        elif input=="LINE(訊息)":
            result=1
        elif input=="線上通話":
            result=2
        elif input=="會面":
            result=3
        elif input=="面對面三人以上會議":
            result=4
        
        return result
        
    def get_minutes_delta(self,input):
        result=1
        if input=="十分鐘":
            result=10
        elif input=="半小時":
            result=30
        elif input=="一小時":
            result=60
        elif input=="兩小時":
            result=120
        elif input=="四小時":
            result=240
        elif input=="八小時":
            result=480
        return result
    def get_day_delta(self,input):
        result=1
        if input=="兩天後":
            result=2
        elif input=="一周後":
            result=7
        elif input=="兩周後":
            result=14
        elif input=="一個月後":
            result=30
        elif input=="一季(三個月)":
            result=92
        elif input=="一年":
            result=365
        
        return result
    def get_customer_activity(self,activity_form,usermanager,isregister):
        msg=None
        if isregister:
            facilityname=activity_form.facility_name
            customername=activity_form.customer_name
            title=activity_form.customer_title
            facility = TFacility.query.filter_by(name=facilityname).first()
            starttime=datetime.strptime(activity_form.starttime, "%Y-%m-%dT%H:%M")
            day_delta=self.get_day_delta(activity_form.timedelta)
            minutes_delta=self.get_minutes_delta(activity_form.minutesdelta)
            type=self.get_type(activity_form.type)
            

            if not facility:
                fac=TFacility()
                fac.id=self.get_id(TFacility.query.count())
                fac.name=facilityname
                db.session.add(fac)
                facility_id=fac.id
                print(facilityname,"已經新建立!",fac)
            else:
                facility_id=facility.id
                print(facilityname+"的資料已經存在資料庫內")
            customer = TCustomer.query.filter_by(name=customername,title=title).first()
            if not customer:
                customer=TCustomer()
                customer.id=self.get_id(TCustomer.query.count())
                customer.ownerid=usermanager.id
                customer.name=customername
                customer.title=title
                customer.facilityid=facility_id
                db.session.add(customer)
                print(customername,"已經新增!",customer)
                
            else:
                print(customername+title+"的資料已經存在資料庫內!")
            act=TActivity()

            act_count=TActivity.query.count()
            id=self.get_id(act_count)
            print("id:",id)
            act.id=id
            
            act.ownerid=usermanager.id
            act.facilityid=facility_id
            act.customerList=str(customer.id)+";"
            act.starttime=starttime
            act.endtime=starttime+timedelta(minutes=minutes_delta)
            
            delta = timedelta(days=day_delta)
            act.nexttime=delta+starttime
            act.type=type
            act.description=activity_form.description
            act.nextstep=activity_form.nextstep
            act.recommand=""

            #supervisor的建議。
            act.status=0
            db.session.add(act)    
            db.session.commit()
            msg=facilityname+customername+title+"新的拜訪資料已經建立!妳好棒!"
            

        return render_template('customer/add_new_activity.html', form=activity_form,msg=msg)
    
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
