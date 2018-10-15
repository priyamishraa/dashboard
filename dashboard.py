from datetime import datetime
import pymysql
from flask import Flask, jsonify, request, render_template, redirect, url_for
from base64 import b64decode, b64encode
from flask_cors import CORS

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

#fetching users from sql       
def fetchingusers():
    try:
        db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
        cursor = db.cursor()
        sql ='''SELECT * FROM UserDetails'''
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    
    except:
        return "Error"
    
    finally:
        cursor.close()
        db.close()

#fetching data from sql 
def fetchingdata():
    try:
        db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
        cursor = db.cursor()
        sql ='''SELECT skExecutionTrackerId, SubTaskMasterId,StepNumber,StepName,TaskMasterID, TaskName,
                DATE(StartTime) AS Start_Date, TIME(StartTime) AS Start_Time,DATE(EndTime) AS End_Date, TIME(EndTime) AS End_Time,
                TaskExecutionTracker.Status, ActualStartTime,TIMEDIFF(TIME(StartTime), ActualStartTime) AS StartTimeDiff,
                TIMEDIFF(TIME(EndTime),TIME(StartTime)) AS TaskExecutionTime, DelayGracePeriodINSec, ErrorAction, EmailTriggerTimeInSec, SMSTriggerTimeInSec, 
                CallTriggerTimeInSec FROM `TaskExecutionTracker`JOIN SubTaskMaster ON 
                TaskExecutionTracker.SubTaskMasterId = SubTaskMaster.bTaskMasterId 
                JOIN TaskMaster ON SubTaskMaster.TaskMasterId = TaskMaster.skMasterId '''
        cursor.execute(sql)
        fetched_data = cursor.fetchall()
        return fetched_data
    
    except:
        return "Error"
    
    finally:
        cursor.close()
        db.close()
        
#converting time in seconds
def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

#decoding Credentials
def decode(data):
    decoded_key = b64decode(data).decode('utf-8')
    return decoded_key

# Route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        sql_userdetails = fetchingusers()
        d = {}
        admin_credentials = []
        #storing user details in dict d
        for row in sql_userdetails:
            value = {'password' : row[2],
                     'designation' : row[3]}
            d[row[1]] = value
        #storing all "admin" credentials in list
        for key,value in d.items():
            values = value
            for key,value in values.items():
                if key == "designation" and value == "admin":
                    for key,value in values.items():
                        if key == "password":
                            admin_credentials.append(value)
        print(admin_credentials)
        #loging in
        for key,value in d.items():
            if request.form['username'] == key:
                values = value
                for key,value in values.items():
                    if key == 'password':
                        decoded_key = decode(value)
                        if request.form['password'] == decoded_key and value in admin_credentials:
                            return redirect(url_for('adminpage'))
                        elif request.form['password'] == decoded_key:
                            return redirect(url_for('homepage'))
                        else:
                            error = 'Username/Password incorrect'
            else:
                error = 'Username/Password incorrect'

    return render_template('index1.html', error=error)

@app.route('/admin')
def adminpage():
    return render_template('admin.html')

@app.route('/home')
def homepage():
    return render_template('welcome.html')

#Creating new account and appending to UserDetails
@app.route('/createaccount', methods=['GET', 'POST'])
def createacc():
    try:
        db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
        cursor = db.cursor()
        Username = request.form.username
        Password = request.form.credentials
        Credentials = b64encode(Password.encode('ascii')).decode('utf-8')
        Designation = request.form.designation
        sql ='''INSERT INTO `UserDetails` (`Username`, `Credentials`, `Designation`) 
                VALUES ("{0}", "{1}", "{2}")'''.format(Username, Credentials, Designation)
        print (sql)
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        print (results)
        return "SUCCESS"
    
    except:
        return "Cannot create account. Some error occured."
    
    finally:
        cursor.close()
        db.close()

#sending data based on requested date
@app.route('/data', methods = ['GET', 'POST'])
def completedata():
    a = fetchingdata()
    d = {}
    if request.method == "POST":
        key = request.form
        today = key["From"]
        print(today)
    for row in a:
        start_time = str(row[7])
        end_time = str(row[9])
        #print(str(row[-1]))
        if str(row[6]) == "2018-04-18":
            FMT = '%H:%M:%S'
            if(start_time != "None"  and end_time != "None"):
                tdelta = datetime.strptime(end_time, FMT) - datetime.strptime(start_time, FMT)
                #print(tdelta)
                value = {'SubTaskMasterID' : str(row[1]),'StepNumber' : str(row[2]),
                             'SubTaskname' : str(row[3]),'TaskMasterID' : str(row[4]),
                             'MainTask' : str(row[5]),'Start_Date' : str(row[6]),
                             'StartTime' : str(row[7]),'End_Date' : str(row[8]),
                             'End_Time' : str(row[9]),'Status' : str(row[10]),
                             'ActualStartTime' : str(row[11]),'starttimediff' : get_sec(str(row[12])),
                             'time_taken' : get_sec(str(tdelta)),'erroraction' : str(row[-4])}
            d[row[0]] = value
        #print(d)
    return jsonify(d)

if __name__ == "__main__":
    app.run(port = '5001')