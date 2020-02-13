from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt   
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy	
from sqlalchemy.sql import func           	
from flask_migrate import Migrate	
import re
app = Flask(__name__)
app.secret_key = "burrito"
bcrypt = Bcrypt(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evently.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')  
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,}$')
# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)
interests = db.Table ('interest',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
                db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key = True),
                db.Column('status',db.String(45)))

followed_users = db.Table ('followed_users',
                db.Column('user_following', db.Integer, db.ForeignKey('user.id'), primary_key = True),
                db.Column('user_being_followed', db.Integer, db.ForeignKey('user.id'), primary_key = True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    fname = db.Column(db.String(45))
    lname = db.Column(db.String(45))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default = func.now())
    update_at = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())
    events_this_user_interest = db.relationship('Event', secondary = interests, backref = 'users_who_interest_event')
    
    users_this_user_is_following = db.relationship('User', secondary = followed_users,
                                                    primaryjoin = 'User.id  == followed_users.c.user_following',
                                                    secondaryjoin= 'User.id == followed_users.c.user_being_followed')
    users_who_follow_this_user = db.relationship('User', secondary = followed_users,
                                                    primaryjoin = 'User.id  == followed_users.c.user_being_followed',
                                                    secondaryjoin= 'User.id == followed_users.c.user_following')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(45))
    description = db.Column(db.String(255))
    location = db.Column(db.String(255))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable = False)
    user = db.relationship('User', foreign_keys =[user_id])
    created_at = db.Column(db.DateTime, server_default = func.now())
    update_at = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())






@app.route("/")
def index():
    if 'userid' in session:
        return redirect('/dashboard')
    else:
        return render_template("index.html")

    
@app.route("/login")
def get_login():
    return render_template("login.html")

@app.route("/register")
def get_register():
    return render_template("register.html")

@app.route("/create-user", methods = ['POST'])
def create_user():
    isValid = True
    
    if len(request.form['fname']) < 1:
    	isValid = False
    	flash("Please enter a first name",'name_error')
    if not (request.form['fname']).isalpha():
    	isValid = False
    	flash("First Name must only contain letters!",'name_error')
    if len(request.form['lname']) < 1:
    	isValid = False
    	flash("Please enter a last name",'last_error')
    if not (request.form['lname']).isalpha():
    	isValid = False
    	flash("Last Name must only contain letters!",'last_error')
    if not EMAIL_REGEX.match(request.form['email']):   
        isValid = False
        flash("Invalid email address!",'email_error')
    if not PASSWORD_REGEX.match(request.form['psw']):   
        isValid = False
        flash("Password must have at least 5 characters, one number, one uppercase character, one special symbol.",'psw_error')
    if request.form['psw'] != request.form['cpsw']:
    	isValid = False
    	flash("Password and Confirm Password should match",'confirm_psw_error')
    
    if isValid:
        user = User(fname = request.form['fname'], lname = request.form['lname'], email = request.form['email'], password = bcrypt.generate_password_hash(request.form['psw']))
        db.session.add(user)
        db.session.commit()
        session['userid'] = user.id
        return redirect('/dashboard')
    return redirect('/register')

@app.route('/dashboard')
def get_dashboard():
    if 'userid' in session:
        return render_template('dashboard.html')
    else :
        return render_template('index.html')
    




if __name__ == "__main__":
    app.run(debug=True)