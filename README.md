# dashboard
import pymysql
from base64 import b64decode
from flask import Flask, jsonify, request
from datetime import datetime
#import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

#User Details List
file1 = open("/home/user/Documents/Task/UserRequestFile.txt", "r")
fields = [x for x in file1.read().split("\n")]


#function for comparing user key with file1 variable
def validate(data):
    decoded_key = b64decode(data).decode('utf-8')
    #print (decoded_key)
    if decoded_key in fields:
        return 1
    else:
        return 0
    

#Fetching data from mysql server
def fetchingdata():
    db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
    cursor = db.cursor()
    sql ='''SELECT skExecutionTrackerId, SubTaskMasterId,StepNumber,StepName,TaskMasterID, TaskName,
            DATE(StartTime) AS Start_Date, TIME(StartTime) AS Start_Time,DATE(EndTime) AS End_Date, TIME(EndTime) AS End_Time,
            TaskExecutionTracker.Status, ActualStartTime,TIMEDIFF(ActualStartTime,TIME(StartTime)) AS DelayGracePeriod,
            TIMEDIFF(TIME(EndTime),ActualStartTime) AS TaskExecutionTime,EmailTriggerTimeInSec, SMSTriggerTimeInSec, 
            CallTriggerTimeInSec FROM `TaskExecutionTracker`JOIN SubTaskMaster ON 
            TaskExecutionTracker.SubTaskMasterId = SubTaskMaster.bTaskMasterId 
            JOIN TaskMaster ON SubTaskMaster.TaskMasterId = TaskMaster.skMasterId '''
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


#converting Run time in seconds
def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


#Complete data    
@app.route('/gooo', methods=['GET'])
def completedata():
#    key = request.headers.get("key")
#    check_validation = validate(key)
  #  if check_validation == 1:
    a = fetchingdata()
    d = {}
    
    for row in a:
        if(str(row[6])=="2018-04-18"):
            value = {'SubTaskMasterID' : str(row[1]),
                             'StepNumber' : str(row[2]),
                             'SubTaskname' : str(row[3]),
                             'TaskMasterID' : str(row[4]),
                             'MainTask' : str(row[5]),
                             'Start_Date' : str(row[6]),
                             'StartTime' : str(row[7]),
                             'End_Date' : str(row[8]),
                             'End_Time' : str(row[9]),
                             'Status' : str(row[10]),
                             'ActualStartTime' : str(row[11]),
                             'time_taken' : str(row[12]),
                             'EmailTriggerTimeInSec' : str(row[13]),
                             'SMSTriggerTimeInSec' : str(row[14]),
                             'CallTriggerTimeInSec' : str(row[15])}
            d[row[0]] = value
            
        #print(d)
    return jsonify(d)



#Completed Tasks
@app.route('/completedtask', methods=['GET'])
def completedtask():
    a = fetchingdata()
    d = {}
    
    for row in a:
        
        start_time = str(row[7])
        end_time = str(row[9])
        if str(row[6])=="2018-04-18":
            FMT = '%H:%M:%S'
            if(start_time !="None"  and end_time!="None"):
                tdelta = datetime.strptime(end_time, FMT) - datetime.strptime(start_time, FMT)
                value = {'SubTaskMasterID' : str(row[1]),
                     'StepNumber' : str(row[2]),
                     'SubTaskname' : str(row[3]),
                     'TaskMasterID' : str(row[4]),
                     'MainTask' : str(row[5]),
                     'Start_Date' : str(row[6]),
                     'StartTime' : str(row[7]),
                     'End_Date' : str(row[8]),
                     'End_Time' : str(row[9]),
                     'Status' : str(row[10]),
                     'ActualStartTime' : str(row[11]),
                     'time_taken' : get_sec(str(tdelta)),
                     'EmailTriggerTimeInSec' : str(row[13]),
                     'SMSTriggerTimeInSec' : str(row[14]),
                     'CallTriggerTimeInSec' : str(row[15])}
                d[str(row[0])] = value
            
    return jsonify(d)

#Error Tasks
@app.route('/errortask', methods=['GET'])
def errortask():
    key = request.headers.get("key")
    check_validation = validate(key)
    if check_validation == 1:
        a = fetchingdata()
        d = {}
        for row in a:
            if (row[10] == "0"):
                delaytime = get_sec(str(row[12]))
                
                if (delaytime >= row [14] & delaytime < row[15]):
                    print('Email Trigger')
                
                if (delaytime >= row [15] & delaytime < row[16]):
                    print('SMS Trigger')
                
                if (delaytime >= row[16]):
                    print('Call Trigger')
                
                value = {'SubTaskMasterID' : str(row[1]),
                         'StepNumber' : str(row[2]),
                         'StepName' : str(row[3]),
                         'TaskMasterID' : str(row[4]),
                         'TaskName' : str(row[5]),
                         'Start_Date' : str(row[6]),
                         'Start_Time' : str(row[7]),
                         'End_Date' : str(row[8]),
                         'End_Time' : str(row[9]),
                         'Status' : str(row[10]),
                         'ActualStartTime' : str(row[11]),
                         'TaskExecutionTime' : str(row[12]),
                         'EmailTriggerTimeInSec' : str(row[13]),
                         'SMSTriggerTimeInSec' : str(row[14]),
                         'CallTriggerTimeInSec' : str(row[15])}
                d[str(row[0])] = value
        
            else:
                return "No error tasks present"
        return jsonify(d)
    
    else:
        return "Invalid Key"


#Filter by date
@app.route('/datefilter' , methods=['POST'])
def datefilter():
    a = fetchingdata()
    d={}
    request_data = request.get_json()
    print(request_data)

    try:
        if "from" in request_data.keys():
            start_date = request_data['from']
        if "to" in request_data.keys():
            end_date = request_data['to']
        print('from :', start_date)
        print('to :', end_date)

    except:
        print ("'from' or 'to' date not specified")


    for row in a:
        try:
            if (str(row[6]) == str(start_date)) or \
                (str(row[6]) == str(end_date)) or \
                (str(row[8]) == str(start_date)) or \
                (str(row[8]) == str(end_date)):
                value = {'SubTaskMasterID' : str(row[1]),
                         'StepNumber' : str(row[2]),
                         'StepName' : str(row[3]),
                         'TaskMasterID' : str(row[4]),
                         'TaskName' : str(row[5]),
                         'Start_Date' : str(row[6]),
                         'Start_Time' : str(row[7]),
                         'End_Date' : str(row[8]),
                         'End_Time' : str(row[9]),
                         'Status' : str(row[10]),
                         'ActualStartTime' : str(row[11]),
                         'TaskExecutionTime' : str(row[12])}
                d[str(row[0])] = value
            else:
                print("Date not found")
    
        except:
            print ("error")

    return jsonify(d)

    
if __name__ == "__main__":
    app.run(port = '5001')
