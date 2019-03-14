from flask import Flask, render_template, flash, request, url_for, redirect, session
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart
from functools import wraps
import gc
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from content import Content
from db_connect import Connection

APP_CONTENT = Content()

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please log in.")
            return redirect(url_for('login'))
        
def login_test(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please log in.")
            return redirect(url_for('login'))
    return decorated_function
    
            

@app.route("/", methods = ["GET","POST"])
def main():
    error = ""
    
    try:
        c, conn = Connection()
        if request.method == "POST":
            
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))
            
            data = c.fetchone()[2]
            
            if sha256_crypt.verify(request.form["password"],data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                
                flash("You are now logged in,"+session['username']+"!")
                return redirect(url_for("dashboard"))
            
            else:
                error = "Invalid credentials, try again."
                
                
        return render_template("main.html", error=error)
    
    except Exception as e:
        flash(e) #remove for production
        error = "Invalid credentials. Try again."
    return render_template("main.html", error = error)


@login_required
@app.route("/dashboard/")
def dashboard():
    return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)

@app.route("/login/", methods = ["GET", "POST"])
    
class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=20)])
    email = TextField("Email Address", [validators.Length(min=6, max=50)])
    password = PasswordField("New Password", [validators.Required(),
                                         validators.EqualTo('confirm')
                                         #message=" Maybe retype your password there, bud. "
                                             ])
    confirm = PasswordField("Repeat Password")
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [validators.Required()])


@app.route("/logout/")
def logout():
    session.clear()
    flash("You've been logged out.")
    gc.collect()
    return redirect(url_for("main"))
    
@app.route("/register/", methods=["GET","POST"])

def register_page():

    try:
        form = RegistrationForm(request.form)
        
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            
            
            c, conn = Connection() #if it runs it will post a string
            
            
            x = c.execute("SELECT * FROM users WHERE username = ('{0}')".format((thwart(username))))
            
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template("register.html", form = form)
            
            else: 
                c.execute("INSERT INTO users (username,password,email,tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username),thwart(password),thwart(email),thwart("/dashboard/")))
                
                
                conn.commit()
                flash("thank u "+username)
                conn.close()
                gc.collect()
                
                session['logged_in'] = True 
                session['username'] = username
                
                return redirect(url_for('dashboard'))
        return render_template("register.html", form = form)
            
            
    except Exception as e:
        return(str(e)) #this is for debugging only remove later
    return("Connected.")

"""Janky code goes here lol """

@app.route("/secret/")
@login_test
def test():
    """
    
    Janky python space
    
    """
    
    return render_template("secret.html", test=test )


## Error Handlers

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")

@app.errorhandler(500)
def int_server_error(e):
    return render_template("500.html", error = e)

if __name__ == "__main__":
	app.run(debug = True)