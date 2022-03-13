from flask import Flask, render_template, request
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import path_calls
import os

t_dir = os.path.abspath('../html')
app = Flask(__name__, template_folder=t_dir)

##Temp database code for SQLalchemy, will need to be changed later for the server SQL
database = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY']   = "tempkey123321"
database.init_app(app)

@app.route('/',methods =["GET", "POST"])
def hello_world():
   if request.methods == "GET":
      return render_template('LoginPage.html')
   elif request.methods == "POST":
      return path_calls.login(request)

@app.route('/news')
def return_news():
   return render_template('news.html')

@app.route('/createaccount',methods =["GET", "POST"])
def create_account() :
   if request.method == "GET" :  # get request for html
      return render_template("CreateAccount.html")
   elif request.method == "POST":  # post requst for form
      return path_calls.create_account(request)

@app.route('/landingpage')
def return_landing_page():
   return render_template('LandingPage.html')

@app.route('/notify')
def return_notify_page():
   return render_template('notify.html')

@app.route('/discover')
def return_discover_page():
   return render_template('discover.html')

if __name__ == '__main__':
   app.run()