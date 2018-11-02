import pymysql
from datetime import datetime,timedelta
from base64 import b64encode, b64decode

class operations():
    #encodes the data 
    def encoding(self, data):
        self.data = data
        return b64encode(data.encode('ascii')).decode('utf-8')
    #decodes the data
    def decoding(self, data):
        self.data = data
        return b64decode(data).decode('utf-8')
        
    
class getdaterange():
    #function returns startdate and enddate in datetime.datetime format
    def get_date_range(self, date):
        self.date = date
        date1 = date
        #print(type(date1), date1)
        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 =  date1 - timedelta(days=1)
        return [date1,date2]

#class conatins functions/methods necessary for fetching data from sql db    
class getdetails():
    #main function which returns data for dashboard       
    def get_details(self, startdate, starttime, enddate, endtime, sortorder, cond):
        self.startdate = startdate
        self.starttime = starttime
        self.enddate = enddate
        self.endtime = endtime
        self.sortorder = sortorder
        self.cond = cond
        startdate=startdate.replace(hour=starttime[0], minute=starttime[1], second=starttime[2])
        #print(startdate)
        enddate=enddate.replace(hour=endtime[0], minute=endtime[1], second=endtime[2])
        #print(enddate)
        if cond =="job":
            #calling function which returns data from startdate to enddate in sort order specified
            a = getdetails().job_fetching_ascending(str(startdate),str(enddate),sortorder)
            #calling function which returns framed data in the form of dictionary
            b = getdetails().framing_data(a)
            return b
#        if cond =="action":
#            #calling function returns data based on action taken
#            a = getdetails().Action_fetching(str(startdate),str(enddate))
#            #calling function which returns framed data in the form of dictionary
#            #b = getdetails().framing_data(a)
#            print(a)
#            return ""
    
    #function fetches data from sql db 
    def job_tracking(startdate, enddate):
        try:
            db = pymysql.connect(host="localhost",user="root",password="tekfriday$",db = "dashboard")
            cursor = db.cursor()
            sql ='''SELECT TaskMasterID,StartTime
            FROM `TaskExecutionTracker`
            JOIN SubTaskMaster ON TaskExecutionTracker.SubTaskMasterId = SubTaskMaster.bTaskMasterId
            JOIN TaskMaster ON SubTaskMaster.TaskMasterId = TaskMaster.skMasterId 
                    WHERE StartTime >="{0}" and StartTime <"{1}" '''.format(startdate,enddate)
            print(sql)
            cursor.execute(sql)
            data_fetched=cursor.fetchall()
            return data_fetched
        except:
            print("error")
        finally:
            cursor.close()
            db.close()
            
    def job_fetching_ascending(startdate, enddate, sortorder):
        try:
            db = pymysql.connect(host="localhost",user="root",password="tekfriday$",db = "dashboard")
            cursor = db.cursor()
            sql ='''SELECT skExecutionTrackerId, SubTaskMasterId,StepNumber,StepName,TaskMasterID, TaskName, 
            StartTime,EndTime,TaskExecutionTracker.Status, ActualStartTime,
            TIMEDIFF(ActualStartTime,TIME(StartTime)) AS DelayTime,
            TIMEDIFF(TIME(EndTime),Time(StartTime)) AS TaskExecutionTime,
            EmailTriggerTimeInSec, `SubTaskMaster`.DelayAction,
            `SubTaskMaster`.ErrorAction FROM `TaskExecutionTracker`
            JOIN SubTaskMaster ON TaskExecutionTracker.SubTaskMasterId = SubTaskMaster.bTaskMasterId
            JOIN TaskMaster ON SubTaskMaster.TaskMasterId = TaskMaster.skMasterId 
                    WHERE StartTime >="{0}" and StartTime <"{1}" {2} '''.format(startdate,enddate,sortorder)
            #print(sql)
            cursor.execute(sql)
            data_fetched= cursor.fetchall()
            return data_fetched
        except:
            print("error")
        finally:
            cursor.close()
            db.close()
    
    #function frames the data fetched from sql db in dictionary format
    def framing_data(self, data_fetched):
        self.data_fetched = data_fetched
        d = {}
        b = 0
        if data_fetched:
            for row in data_fetched:
                value = {'SubTaskname' : str(row[3]),
                     'MainTask' : str(row[5]),
                     'Start_Date' : str(row[6]),
                     'End_Date' : str(row[7]),
                     'Status' : str(row[8]),
                     'DelayAction':str(row[13]),
                     'ErrorAction':str(row[14]),
                     'ActualStartTime':str(row[9])
                     }
                d[b] = value
                b +=1
        #print(d)
        return d

    #fetches data from Action_tracker database in mysql
    def Action_fetching(self, startdate, enddate):
        try:
            self.startdate = startdate
            self.enddate = enddate
            db = pymysql.connect(host="localhost",user="root",password="root",db = "dashboard")
            cursor = db.cursor()
            sql ='''SELECT * from Action_tracker
                    WHERE Actual_time_to_start >="{0}" and Actual_time_to_start <"{1}"  '''.format(startdate,enddate)
            #print(sql)
            cursor.execute(sql)
            data_fetched= cursor.fetchall()
            return data_fetched
        except:
            print("error")
        finally:
            cursor.close()
            db.close()

#class conating functions/methods related to user
class userdetails():
    #fetches users from UserDetails db 
    def fetchingusers(self):
        try:
            db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
            cursor = db.cursor()
            sql ='''SELECT * FROM UserDetails'''
            cursor.execute(sql)
            user_fetched = cursor.fetchall()
            return user_fetched
        
        except:
            return "Error"
        
        finally:
            cursor.close()
            db.close()
    
    #stores all admin usernames in the form of list 
    def admincreds(self):
        user_fetched = userdetails().fetchingusers()
        admin_username = []
        d = {k:a for k,v,a in user_fetched}
        for key, value in d.items():
            if "Admin" in value:
                admin_username.append(key)
        return admin_username
    
    #loggingin 
    def loggingin(self, username, password):
        self.username = username 
        self.password = password
        credentials = operations().encoding(password)
        admin_username = userdetails().admincreds()
        user_fetched = userdetails().fetchingusers()
        d = {k:v for k,v,a in user_fetched}
        if username in d and credentials == d[username] and username in admin_username:
            return 1
        elif username in d and credentials == d[username]:
            return 2
        else:
            return 3
        
    #adds user to the UserDetails db while creating new account
    def addinguser(self, username, password, designation):
        self.username = username
        self.password = password
        self.designation = designation
        try:
            db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
            cursor = db.cursor()
            credentials = operations().encoding(password)
            sql ='''INSERT INTO `UserDetails` (`Username`, `Credentials`, `Designation`) 
                    VALUES ("{0}", "{1}", "{2}")'''.format(username, credentials, designation)
            print (sql)
            cursor.execute(sql)
            db.commit()
            return 0
    
        except:
            return 1
        
        finally:
            cursor.close()
            db.close()
