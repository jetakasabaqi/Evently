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
    entry = db.Column(db.String(255))
    event_date = db.Column(db.DateTime, server_default = func.now())
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

@app.route("/friends")
def get_friends():
    if 'userid' not in session:
        return redirect('/')
    users = User.query.all()
    this_user = User.query.filter_by(id = session['userid']).first()

    users_following = this_user.users_this_user_is_following

    for user in users:
        print(user.id)
        print([user.id for user in users_following])
        if user.id in [user.id for user in users_following]:
            user.following= True
            print(user.following)
 
    users.remove(this_user)
   
    return render_template("friends.html", users = users)
@app.route("/add-friend/<user_id>")
def add_friend(user_id):
    user = User.query.filter_by(id = session['userid']).first()
    new_friend = User.query.filter_by(id = user_id).first()
    user.users_this_user_is_following.append(new_friend)
    db.session.commit()
    return redirect('/friends')

@app.route("/unfriend/<user_id>")
def unfriend(user_id):
    user = User.query.filter_by(id = session['userid']).first()
    the_friend = User.query.filter_by(id = user_id).first()
    user.users_this_user_is_following.remove(the_friend)
    db.session.commit()
    return redirect('/friends')

@app.route("/events")
def get_events():
    if 'userid' not in session:
        return redirect('/')
    user = User.query.filter_by(id = session['userid']).first()
    users = User.query.all()
    users_following = user.users_this_user_is_following
    events = Event.query.all()
    users_ids = [user.id for user in users]
#only show events from users not following
    for user in users:
        if user in users_following:
            users.remove(user)
    


    for event in events:
        if event.user_id in users_ids:
            events.remove(event)
            
    for event in events:
        if event.user_id == session['userid']:
            events.remove(event)
       
    return render_template("events.html", events = events)

@app.route("/profile")
def get_profile():
    if 'userid' not in session:
        return redirect('/')
  
    user = User.query.filter_by(id = session['userid']).first()
    events_created = Event.query.filter_by(user_id = session['userid']).all()
    events_attended = user.events_this_user_interest
    

    return render_template("profile.html", user = user, events_created = events_created,events_attended = events_attended, events_created_count = len(events_created),events_attended_count = len(events_created))

@app.route("/login-user", methods  =['POST'])
def login_user():
    isValid = True

    if len(request.form['email']) < 1:
        isValid = False
        flash("Please enter an email","email_error")
    if len(request.form['password']) <1:
        isValid = False
        flash("Please enter a password","password_error")
    
    if isValid:
        user = User.query.filter_by(email =request.form['email']).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                session['userid'] = user.id
                return redirect('/dashboard')
        flash("Email or Password is wrong","login_error")
    return redirect('/login')


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
        events = Event.query.all()
        user = User.query.filter_by(id = session['userid']).first()

        events_with_status = db.session.execute(f"select * from interest where user_id ={session['userid']}")
        users_following = user.users_this_user_is_following

        for event_status in events_with_status:
            for event in events:
                if event_status.event_id == event.id:
                    event.interes = event_status.status

        for event in events:
            if event.user_id not in [user.id for user in users_following] and event.user_id != session['userid']:
                events.remove(event)
                
        return render_template('dashboard.html', events = events)
    else :
        return render_template('index.html')

@app.route("/create-event", methods = ['POST'])
def create_event():
    event = Event(name=request.form['name'], description = request.form['description'], location = request.form['location'], entry = request.form['entry'],event_date =    datetime.strptime(request.form['date'], '%Y-%m-%d'),user_id = session['userid'])
 
    db.session.add(event)
    db.session.commit()
    return redirect('/profile')

@app.route("/interest", methods = ['POST'])
def interest_event():
    string = request.form['value']
    interes = string[0]
    event_id = string[1]
    event = Event.query.filter_by(id  = event_id).first()
    user = User.query.filter_by(id  = event_id).first()
    if event in user.events_this_user_interest:
         db.session.execute(interests.update().values(user_id=session['userid'],event_id=event_id, status = interes))
    else:
        db.session.execute(interests.insert().values(user_id=session['userid'],event_id=event_id, status = interes))
    db.session.commit()
    return redirect('/')
    

@app.route('/logout')
def logout_user():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)