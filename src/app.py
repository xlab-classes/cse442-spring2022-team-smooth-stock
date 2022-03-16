from flask import Flask, render_template, request
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os



t_dir = os.path.abspath('../html')
app = Flask(__name__, template_folder=t_dir)

##Temp database code for SQLalchemy, will need to be changed later for the server SQL
database = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY']   = "tempkey123321"
database.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

import data_structures as DS
import path_calls

@app.route('/',methods =["GET", "POST"])
def login():
   if request.method == "GET":
      return render_template('LoginPage.html')
   elif request.method == "POST":
      return path_calls.login(request)


@app.route('/news')
def return_news():
   return render_template('news.html')

@app.route('/create_account',methods =["GET", "POST"])
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


@app.route('/test_login')
@login_required
def test_login():
   return ("You are logged in!")

@login_manager.user_loader
def user_loader(user_id):
   return DS.Account.query.get(int(user_id))

if __name__ == '__main__':
   app.run()