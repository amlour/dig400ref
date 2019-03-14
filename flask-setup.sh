#!/bin/bash
#Gets updates and installs apache WSGI
sudo apt-get update
sudo apt-get install apache2

sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod wsgi

#Creates the basic Flask Directory
cd /var/www
sudo mkdir FlaskApp
cd FlaskApp
sudo mkdir FlaskApp
cd FlaskApp
sudo mkdir static templates

#Creates the init file on the current users desktop
#cat <<EOF >/var/www/FlaskApp/FlaskApp/__init__.py
#from flask import Flask
#app = Flask(__name__)

#@app.route("/")
#def index():
#    return "hello world!"

#if __name__=="__main__":
#    app.run()
#EOF

#Set py3 as default
ln -sf /usr/bin/python3 /usr/bin/python

#Configure Python
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install Flask

#Create the config file
#ADD YOUR OWN IP (ServerName) AND EMAIL (ServerAdmin) HERE!!
cat <<EOF >/etc/apache2/sites-available/FlaskApp.conf
<VirtualHost *:80>
  ServerName 127.0.0.1
  ServerAdmin youemail@email.com
  WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
  <Directory /var/www/FlaskApp/FlaskApp/>
    Order allow,deny
    Allow from all
  </Directory>
  Alias /static /var/www/FlaskApp/FlaskApp/static
   <Directory /var/www/FlaskApp/FlaskApp/static/>
    Order allow,deny
    Allow from all
  </Directory>
  ErrorLog ${APACHE_LOG_DIR}/error.log
  LogLevel warn
  CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF

sudo a2ensite FlaskApp
sudo service apache2 restart

#Setup WSGI
cat <<EOF >/var/www/FlaskApp/flaskapp.wsgi
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/")

from FlaskApp import app as application
application.secret_key = 'something super DUPER secret'
EOF

sudo service apache2 restart