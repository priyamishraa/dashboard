from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from support_functions import getdetails, getdaterange, userdetails
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True


# current running jobs
@app.route('/jobs_today', methods=['GET', 'POST'])
def jobs():
    if(request.method == 'POST'):
        date1 = (datetime.now()).strftime("%Y-%m-%d")
        date = getdaterange().get_date_range(date1)
        p = request.form["filter"]
        print(p)
        d = getdetails().get_details(date[1], [23, 59, 59], date[0], [23, 59, 59], "order by {0} ASC".format(p), str("job"))
        # a = get_details(date[1], [23, 59, 59], date[0], [23, 59, 59], "order by {0} ASC".format(p), str("action"))
        return(jsonify(d))


# jobs in a given date range
@app.route('/date_range', methods=['GET', 'POST'])
def date_range():
    if request.method == 'POST':
        try:
            date1 = request.form["From"]
            date2 = request.form["To"]
            p = request.form["filter"]
            date1 = datetime.strptime(date1, "%Y-%m-%d")
            date2 = datetime.strptime(date2, "%Y-%m-%d")
        except:
            if date1 == "" and date2 == "" and p == "":
                return "Please select StartDate, EndDate, and Filter"
            if p == "":
                p = "StartTime"
            if date1 == "" and date2 != "" and p != "":
                date2 = datetime.strptime(date2, "%Y-%m-%d")
                date1 = date2
            if date2 == "" and date1 != "" and p != "":
                date2 = date1
    return(jsonify(getdetails().get_details(date1, [00, 00, 00], date2, [23, 59, 59], "order by StartTime ASC".format(p), str("job"))))


# error jobs on a particular date
@app.route('/error_jobs', methods=['GET', 'POST'])
def error_jobs():
    if request.method == 'POST':
        date = getdaterange().get_date_range(request.form["Date"])
        print(date)
        return (jsonify(getdetails().get_details(date[1], [23, 59, 59], date[0], [23, 59, 59], "and TaskExecutionTracker.Status =0", "job")))


# login page route
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        a = userdetails().loggingin(username, password)
        if a == 1:
            return redirect(url_for('adminpage'))
        elif a == 2:
            return redirect(url_for('homepage'))
        else:
            error = 'Username/Password incorrect'
        
    return render_template('index1.html', error=error) 

# admin page route
@app.route('/admin')
def adminpage():
    return render_template('admin.html')


# user page route
@app.route('/home')
def homepage():
    return render_template('welcome.html')


# Creating new account and appending to UserDetails
@app.route('/createaccount', methods=['GET', 'POST'])
def createacc():
    error = None
    if request.method == 'POST':
        Username = request.form["username"]
        Password = request.form["credentials"]
        Designation = request.form["designation"]
        user = userdetails().addinguser(Username, Password, Designation)
        if user == 0:
            return "Account Created Successfully"
        else:
            error = "Cannot create account. Some error occured."
        return render_template('createacc.html', error=error)

if __name__ == "__main__":
    app.run(port=5001)
