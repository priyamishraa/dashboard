from flask import Flask, render_template, redirect, url_for, request, jsonify
import os
import pymysql
from base64 import b64encode, b64decode

app = Flask(__name__)
app.config["DEBUG"] = True

 
def fetchingdata():
    db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
    cursor = db.cursor()
    sql ='''SELECT * FROM UserDetails'''
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def encode(data):
    encoded_key = b64encode("b"+data).decode('utf-8')
    return encoded_key

def decode(data):
    decoded_key = b64decode(data).decode('utf-8')
    return decoded_key
         
    
@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('welcome.html')


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        a = fetchingdata()
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
        for key,value in d.items():
            if request.form['username'] == key:
                values = value
                for key,value in values.items():
                    if key == 'password':
                        decoded_key = decode(value)
                        if request.form['password'] == decoded_key and value in l:
                            return redirect(url_for('admin'))
                        elif request.form['password'] == decoded_key:
                            return redirect(url_for('home'))
                            
                        else:
                            error = 'Username/Password incorrect'
            else:
                error = 'Username/Password incorrect'

    return render_template('index1.html', error=error)


@app.route('/admin', methods=['GET', 'POST'] )
def admin():
    if request.method == 'POST':
        if request.id == 'createacc':
            return redirect(url_for('createaccount'))
        elif request.id == 'logout':
            return redirect(url_for('login'))
    return render_template('admin.html')

        
@app.route('/createaccount')
def createacc():
#    error = None
#    if request.method == 'POST':
#        email = request.form['email']
#        password = request.form['password']
#        passrepeat = request.form['passrepeat']
#        if password == passrepeat:
#            credentials = encode(password)
#            db = pymysql.connect("localhost","root","tekfriday$","dashboard" )
#            cursor = db.cursor()
#            sql ='''INSERT INTO UserDetails 
#                    values (6, email = %s, credentials = %s, "user" '''
            
    return render_template('createacc.html')

        
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=5001)