
from apps import db
from flask import render_template
#所有資料的介面
class TCustomerDataFake():
    usermanager="操作(使用)者名稱"
    current_patientid="病人姓名"
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
