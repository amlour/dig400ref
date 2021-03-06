from flask import Flask, render_template, flash, request, url_for, redirect, session, make_response, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators
import sqlite3 as lite
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart
from functools import wraps
from datetime import datetime, timedelta
import gc
import os, sys; 

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from werkzeug.utils import secure_filename

from content import Content
from db_connect import Connection

APP_CONTENT = Content()

UPLOAD_FOLDER = "/var/www/FlaskApp/FlaskApp/uploads"

ALLOWED_EXTENSIONS = set(["txt", "png", "jpg", "jpeg", "gif"])

app = Flask(__name__)

app.config['SECRET_KEY'] = 'soveryverysecret'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DATABASE = "/var/www/FlaskApp/FlaskApp/database_example/database_example.db"

def message(user_name,message):
    con = lite.connect(DATABASE)
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS input_log (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT, message TEXT)")
    c.execute("INSERT INTO input_log (user_name,message) VALUES (?,?)",(user_name, message))
    con.commit()
    c.close()
    return

def contents():
    con = lite.connect(DATABASE)
    c = con.cursor()
    c.execute("SELECT * FROM input_log")
    rows = c.fetchall() # there is also fetchone() this returns a list
    con.close()
    return reversed(rows)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('main'))
    return wrap

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  

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



@app.route("/dashboard/")
@login_required
def dashboard():
    return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)

@app.route("/profile/")
def profile():
    return render_template("profile.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/tos/")
def tos():
    return render_template("tos.html")

@app.route("/resources/")
def resources():
    return render_template("resources.html")

@app.route("/announcements/")
def announcements():
    return render_template("announcements.html", APP_CONTENT = APP_CONTENT)

@app.route("/message/", methods=["GET", "POST"])
@login_required
def message_page():
    try:
        content = ""
        if request.method == "POST":
           
            data = thwart(request.form['message'])
           
            name = session['username']
           
            message(name, data)
           
            content = contents()
            flash("Thanks for your message!")
            return render_template("message.html", content = content)
       
        content = contents()
        return render_template("message.html", content = content)
   
    except Exception as e:
        return str(e) # remember to remove! For debugging only!


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
@login_required
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
@login_required
def secret():
    try:
        #the python goes here!
        
        def function_i_guess():
            output = ["DIGIT 400 is good", "Python, Java, PHP, SQL, C++", "<p><strong>hello world</strong></p>", 42, "42"]
            return output
        
        output = function_i_guess()
    
        return render_template("secret.html", output = output)
    except Exception as e:
        return str(e)


    
""" janky code ends here """

@app.route('/sitemap.xml/', methods=["GET"])
def sitemap():
    try:
        pages = []
        week = (datetime.now() - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            pages.append(["http://157.230.50.193"+str(rule.rule), week])
        
        sitemap_xml = render_template('sitemap_template.xml', pages = pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    
    except Exception as e:
        return(str(e))


@app.route("/uploads/", methods=["GET","POST"])
@login_required
def upload_file():
    try:
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["file"]
            
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                flash("File "+ str(filename) +" upload successful!")
                return render_template('uploads.html', filename = filename)
        return render_template("uploads.html")
    except Exception as e:
        return str(e) # remove for production

@app.route("/download/")
@login_required
def download():
    try:
        return send_file("/var/www/FlaskApp/FlaskApp/uploads/dog.jpeg", attachment_filename="doggie.jpeg")
    except Exception as e:
        return str(e)

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

if __name__ == '__main__':
    app.run(debug=True)