from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import MySQLdb.cursors
import re
app = Flask(__name__)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'
# Enter your database connection details below
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='root'
app.config['MYSQL_DATABASE_DB']='eventmanagement'
# Intialize MySQL
mysql = MySQL(app)
# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/admin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        # If account exists in accounts table in out database
        if username=='admin' and password=='admin':
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = 0
            session['username'] = username
            # Redirect to home page
            return redirect(url_for('adminhome'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)
# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    if request.method=='POST':
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    #if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
    # Create variables for easy access
        fullname = request.form['fname']
        cname = request.form['cname']
        roll = request.form['rno']
        mobile=request.form['mobile']
        email = request.form['email']
        evt=request.form['eventname']
        # Check if account exists using MySQL
        cursor = mysql.get_db().cursor()
        e='insert into '+evt+' (fullname,classname,rollno,mobile,email)values(%s,%s,%s,%s,%s)'
        cursor.execute(e,(fullname,cname,roll,mobile,email))
        mysql.get_db().commit()
        cursor.close()
        msg='Registered to event successfully'
    return render_template('register.html', msg=msg)
# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/admin/events', methods=['GET', 'POST'])
def adminhome():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM events order by id desc')
        events = cursor.fetchall()
        if request.method=="POST":
            if 'delete' in request.form:
                b=request.form['delete']
                ab='drop table '+b
                cursor.execute(ab)
                cursor.execute("delete from events where evtname=%s",(b,))
                mysql.get_db().commit()
                cursor.close()
                return redirect(url_for('adminhome'))
            if 'event' in request.form:
                a=request.form['event']
                cursor = mysql.get_db().cursor()
                e='select * from '+a
                cursor.execute(e)
                participants=cursor.fetchall()
        # We need all the account info for the user so we can display it on the profile page
        # Show the profile page with account info
                return render_template('participants.html',participants=participants)
        # User is loggedin show them the home page
        return render_template('adminhome.html', events=events)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/', methods=['GET', 'POST'])
def home():
    # Check if user is loggedin
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM events order by id desc')
    events = cursor.fetchall()
    if request.method=="POST":
        a=request.form['event']
        return render_template('register.html',a=a)    
    cursor.execute('select evtname from events')
    ename=cursor.fetchall()
    return render_template('home.html',events=events)
    # User is not loggedin redirect to login page
# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/admin/addevent', methods=['GET', 'POST'])
def addevent():
    msg=''
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == "POST":
            eventname=request.form['ename']
            departname=request.form['dname']
            description=request.form['desc']
            cursor = mysql.get_db().cursor()
            cursor.execute('insert into events(evtname,dptname,description)values(%s,%s,%s)',(eventname,departname,description))
            evt='create table ' +eventname+' (id int NOT NULL AUTO_INCREMENT PRIMARY KEY,fullname varchar(30),classname varchar(30),rollno varchar(30),mobile varchar(30),email varchar(30))'
            cursor.execute(evt)
            mysql.get_db().commit()
            cursor.close()
            msg='Event added successfully!'
        # We need all the account info for the user so we can display it on the profile page
        # Show the profile page with account info
        return render_template('addevent.html',msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
