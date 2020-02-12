from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt   
from datetime import datetime 
import re
app = Flask(__name__)
app.secret_key = "burrito"

@app.route("/")
def index():
    return render_template("index.html")

    
@app.route("/login")
def get_login():
    return render_template("login.html")

@app.route("/register")
def get_register():
    return render_template("register.html")




if __name__ == "__main__":
    app.run(debug=True)