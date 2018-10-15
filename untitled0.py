import pymysql

from flask import Flask, render_template, redirect, url_for, request, jsonify

from datetime import datetime
#import datetime
from flask_cors import CORS
from base64 import b64decode

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)


def fetchingdata():
    db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
    cursor = db.cursor()
    sql ='''SELECT skExecutionTrackerId, SubTaskMasterId,StepNumber,StepName,TaskMasterID, TaskName,
            DATE(StartTime) AS Start_Date, TIME(StartTime) AS Start_Time,DATE(EndTime) AS End_Date, TIME(EndTime) AS End_Time,
            TaskExecutionTracker.Status, ActualStartTime,TIMEDIFF(ActualStartTime,TIME(StartTime)) AS DelayGracePeriod,
            TIMEDIFF(TIME(EndTime),ActualStartTime) AS TaskExecutionTime,EmailTriggerTimeInSec, SMSTriggerTimeInSec, 
            CallTriggerTimeInSec,ErrorAction FROM `TaskExecutionTracker`JOIN SubTaskMaster ON 
            TaskExecutionTracker.SubTaskMasterId = SubTaskMaster.bTaskMasterId 
            JOIN TaskMaster ON SubTaskMaster.TaskMasterId = TaskMaster.skMasterId '''
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def fetchingusers():
    db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
    cursor = db.cursor()
    sql ='''SELECT * FROM UserDetails'''
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def decode(data):
    decoded_key = b64decode(data).decode('utf-8')
    return decoded_key

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def completedtask(todayp):
    a = fetchingdata()
    d = {}
    #print(today)
    for row in a:
        
        start_time = str(row[7])
        end_time = str(row[9])
        print(str(row[-1]))
        if str(row[6])==today:
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
                     'CallTriggerTimeInSec' : str(row[15]),
                     'ErrorAction':str(row[-1])
                     }
                d[str(row[0])] = value
    return d

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        a = fetchingusers()
        d = {}
        l = []
        for row in a:
            value = {'password' : row[2],
                     'designation' : row[3]}
            d[row[1]] = value
        for key,value in d.items():
            values = value
            for key,value in values.items():
                if key == "designation" and value == "admin":
                    for key,value in values.items():
                        if key == "password":
                            l.append(value)
        print(l)
        user=request.form['username']
        pwd=request.form['password']
        for key,value in d.items():
            
            if user == key:
                values = value
                for key,value in values.items():
                    if key == 'password':
                        decoded_key = decode(value)
                        if pwd == decoded_key and value in l:
                            return render_template("admin.html")#admin page
                        
                        elif pwd == decoded_key:
                            return render_template("welcome.html")#user page
                            
                        else:
                            error = 'Username/Password incorrect'
            else:
                error = 'Username/Password incorrect'

    return render_template('index1.html', error=error)
    
    
    
    
  
@app.route('/gooo', methods=['POST','GET'])
def completedata():
    global today
    if request.method == "POST":
        key = request.form
        today = key["From"]
        print(today)
        #print(a)
    return jsonify("helo")

@app.route('/completedtask', methods=['GET','POST'])
def completedta():
    global today
    print(today)
    a = completedtask(today)
    return jsonify(a)
    
    
if __name__ == "__main__":
    app.run()