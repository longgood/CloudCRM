from apps.authentication.models import TFacility,TEvent,TCustomer, TManager
#from apps import db
from flask import render_template
from datetime import datetime , timedelta
from apps.reports.datas import TData
import random
reportdata=TData()
#所有資料的介面
class TCustomerData():
    usermanager="操作(使用)者名稱"
    current_patientid="病人姓名"
    """
    def get_id(self,num):
        pre=random.randint(10,99)
        id=pre+num*100+1000000000
        return id
    """
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
        elif input=="手動輸入":
            resultd=10
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
    def get_priority(self,input):
        print("回傳的數值:",input)
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

    def get_customertype(self,input):
        result=0
        if input=="臨床":
            result=0
        elif input=="投資人":
            result=1
        elif input=="經銷商":
            result=2
        return result

    def get_customer_event(self,event_form,usermanager,isregister):
        msg=None
        if isregister:
            facilityname=event_form.facility_name
            customername=event_form.customer_name
            title=event_form.customer_title
            facility = TFacility.query.filter_by(displayName=facilityname).first()
            starttime=datetime.strptime(event_form.starttime, "%Y-%m-%dT%H:%M")
            
            
            day_delta=self.get_day_delta(event_form.timedelta)
            minutes_delta=self.get_minutes_delta(event_form.minutesdelta)
            type=self.get_type(event_form.type)
            
            print("FacilityName:",facilityname,",F:",facility)
            if not facility:
                fac=TFacility({})
                #fac.uid=self.get_id(TFacility.query.count())
                fac.displayName=facilityname
                fac.add_new()
                facility_id=fac.uid
                print("facility add",fac.uid,fac.key,fac.displayName)
            else:
                facility_id=facility.uid

            customer = TCustomer.query.filter_by(realName=customername,jobTitle=title).first()
            if not customer:
                customer=TCustomer()
                customer.managerID=usermanager.uid
                customer.realName=customername
                customer.jobTitle=title
                customer.facilityID=facility_id
                customer.add_new()
                print("customer add")
                
                
            else:
                print(customername+title+"的資料已經存在資料庫內!")
            event=TEvent()
            eventdic={"managerID":usermanager.uid,"facilityID":facility_id,"customerID":customer.uid,"startTime":starttime,"endTime":starttime+timedelta(minutes=minutes_delta),
                    "nextTime":timedelta(days=day_delta)+starttime,"type":type,"description":event_form.description,"nextStep":event_form.nextstep,"recommand":"",
                    "winrate":50,"priority":50}
            
            event.add_new(eventdic)
            """
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
            act.update()
            #db.session.add(act)    
            #db.session.commit()
            """
            msg=facilityname+customername+title+"新的拜訪資料已經建立!妳好棒!"
            
                            
        return render_template('customer/add_new_activity.html', form=event_form,msg=msg)
    def cal_customer_activity_adding_mode(self,activity_form,usermanager,isregister):
        msg=None
        print("--001cal_customer_activity_adding_mode--",isregister)
        if isregister:
            facilityname=activity_form.facility_name
            customername=activity_form.customer_name
            title=activity_form.customer_title
            facility = TFacility.query.filter_by(displayName=facilityname).first()
            starttime=datetime.strptime(activity_form.starttime, "%Y-%m-%dT%H:%M")
            day_delta=self.get_day_delta(activity_form.timedelta)
            minutes_delta=self.get_minutes_delta(activity_form.minutesdelta)
            type=self.get_type(activity_form.type)
            priority=self.get_priority(activity_form.priority)
            winrate=self.get_priority(activity_form.winrate)
            customerType=self.get_customertype(activity_form.customerType)
            
            print("--002 cal_customer_activity_adding_mode:Facility:",facility)
        
            if not facility:
                fac=TFacility()
                #fac.uid=self.get_id(TFacility.query.count())
                fac.displayName=facilityname
                fac.add_new()
                facility_id=fac.uid
                print("--002沒有facility但已經新增",fac)

            else:
                facility_id=facility.uid
            customer = TCustomer.query.filter_by(realName=customername,jobTitle=title).first()
            print("姓名:",customername,",取得:",customer.realName)
            if not customer:
                customer=TCustomer()
                #customer.uid=self.get_id(TManager.query.count())
                customer.ownerid=usermanager.uid
                customer.name=customername
                customer.title=title
                customer.facilityid=facility_id
                customer.add_new()
                
                

                #db.session.add(customer)
                
            else:
                print(customername+title+"的資料已經存在資料庫內!")
           
            
            
            event=TEvent()
            act_count=TEvent.query.count()

         
            actdic={"managerID":usermanager.uid,"facilityID":facility_id,"customerID":customer.uid,"startTime":starttime,"endTime":starttime+timedelta(minutes=minutes_delta),
                    "nextTime":timedelta(days=day_delta)+starttime,"type":type,"description":activity_form.description,"nextStep":activity_form.nextstep,"recommand":"","status":0,
                    "winrate":winrate,"priority":priority}
            event.add_new(actdic)
           
            msg=facilityname+customername+title+"新的拜訪資料已經建立!妳好棒!"
        return activity_form,msg
    def get_customer_activity_adding_mode(self,form,usermanager,isregister):
        now_dt = datetime.today() 
        now_dt_format = now_dt.strftime('%Y-%m-%dT%H:%M')
        facility_name=""
        customer_title=""
        cust=TCustomer.query.filter_by(realName=form.customer_name).first()
        if cust:
            customer_title=cust.jobTitle
            fac=TFacility.query.filter_by(uid=cust.facilityID).first()
            if fac:
                print("輸出",fac)
                facility_name=fac.displayName
            else:
                print("Fail Facility")
        else:
            print("Fail Customer")
        
        form.facility_name=facility_name
        form.customer_title=customer_title
        form.starttime=now_dt_format

        form.type="手動輸入"
        form.minutesdelta="十分鐘"
        
        activity_form,msg=self.cal_customer_activity_adding_mode(form,usermanager,isregister)
        result_facility=reportdata.cal_report_facility_user(usermanager)
        print("----------------------------end")
        return render_template('customer/add_new_activity_adding_mode.html', form=activity_form,msg=msg,activity=result_facility)
    #後續跟進
    def get_customer_followup(self,usermanager):
        ownerid=usermanager.uid
        result=TEvent.query.filter(TEvent.managerID==ownerid,TEvent.nextTime>timedelta(days=1) ).all()
        cust_followed=[]
        eventlist=[]
        for r in result:
            #之後有跟進就以此為主。
            customerid=r.customerID
            if customerid not in cust_followed:
                cust_followed.append(customerid)
                followed=TEvent.query.filter(TEvent.managerID==ownerid,TEvent.customerLIST==r.customerLIST,TEvent.startTime>r.startTime  ).first()
                if followed:
                    customerid=followed.customerID
                    cust=TCustomer.query.filter_by(uid=customerid).first()
                    eventlist.append(followed)
                else:
                    customerid=r.customerID
                    cust=TCustomer.query.filter_by(uid=customerID).first()
                    eventlist.append(r)
        
        for event in eventlist:
            customerid=event.customerID
            cust=TCustomer.query.filter_by(uid=customerid).first()
            
            fac=TFacility.query.filter_by(uid=event.facilityID).first()
        
        
        return ""
    def get_new_device(self,name):

        
        
        return render_template('customer/register_device.html')