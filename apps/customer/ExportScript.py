import json
class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
def export_class(item,filename="typename"):
    file = open(filename+".txt", "w",encoding='UTF-8')
    for f in item:
        dictionary=f.__dict__
        dictionary.pop('_sa_instance_state', None)
        str=json.dumps(dictionary,  ensure_ascii=False, cls=DatetimeEncoder)
        file.writelines(str+"\n")
    file.close()

from apps.authentication.models import TFacility,TActivity,TCustomer,TProject,TDevice,Users

def crm_database():

    export_class(Users.query.all(),"users")    
    export_class(TFacility.query.all(),"tfacility")
    export_class(TActivity.query.all(),"tactivity")
    export_class(TCustomer.query.all(),"tcustomer")
    
    string="done"
    return string
def crm_read():
    filename="D:\\_Projects\\CloudCRM\\tfacility.txt"
    fp = open(filename, "r",encoding='UTF-8')
    lines=fp.readlines()
    fp.close()
    for i in range(len(lines)):
        dic=json.loads(lines[i])
        fac=TFacility(dic)
        print(lines[i],type(dic),",類別:",type(fac))
        
    return lines