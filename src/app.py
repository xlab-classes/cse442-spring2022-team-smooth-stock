from re import L
from flask import Flask, render_template, request, session
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import connect, Error
import mysql.connector
import os
import requests
import json
import smtplib
import time


t_dir = os.path.abspath('../html')
app = Flask(__name__, template_folder=t_dir)

##Temp database code for SQLalchemy, will need to be changed later for the server SQL
database = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY']   = "tempkey123321"
database.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login_needed'
login_manager.init_app(app)

mydb = mysql.connector.connect(
   host="oceanus.cse.buffalo.edu",
   user="kptodd",
   password="50318271",
   database="cse442_2022_spring_team_q_db"
)


import data_structures as DS
import path_calls



@app.route('/',methods =["GET", "POST"])
def login():
   if request.method == "GET":
      return render_template('LoginPage.html')
   elif request.method == "POST":
      return path_calls.login(request)

@app.route('/login_needed')
def login_needed():
   return render_template('LoginPage.html', error = "Access denied, login required.")

@app.route('/news')
#@login_required
def return_news():
   xml = path_calls.parse_xml()
   return render_template('news.html', title=xml)

@app.route('/create_account',methods =["GET", "POST"])
def create_account() :
   if request.method == "GET" :  # get request for html
      return render_template("CreateAccount.html")
   elif request.method == "POST":  # post requst for form
      return path_calls.create_account(request)

@app.route('/landingpage')
def return_landing_page():
   return render_template('LandingPage.html')


def email(sender_to, message):
   gmail_user = 'smoothstocks1@gmail.com'
   gmail_password =  '!qazxsw23'
   # email_text = """\
   # From: %s
   # To: %s
   # Subject: %s

   # %s
   # """ % (gmail_user, ", ".join(to), "stocks", email_message)

   try:
      smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
      smtp_server.ehlo()
      smtp_server.login(gmail_user, gmail_password)
      smtp_server.sendmail(gmail_user, sender_to, message)
      smtp_server.close()
      print ("Email sent successfully!")
   except Exception as ex:
      print ("Something went wrong….",ex)


def where(stock, name, username,cursor, newprice, plusminus):
   if stock == name:
      cursor.execute("SELECT email, username FROM userdata")
      myresults = cursor.fetchall()

      for s in myresults:
         print(s[1])
         if username==s[1]:
            print(s[0])
            email(s[0], stock+" price change!\n"+"New price: "+str(newprice)+"\n"+"Change By: "+str(plusminus))
            return True
   return False

def parse_information(name, newprice, plusminus):
   mydb = mysql.connector.connect(
         host="oceanus.cse.buffalo.edu",
         user="dtan2",
         password="50278774",
         database="cse442_2022_spring_team_q_db"
      )
   cursor = mydb.cursor()

   cursor.execute("SELECT username, stocks FROM saved_stocks")
   myresult = cursor.fetchall()

   for x in myresult:
      arr_stock = x[1].split(", ")
      username = x[0]
      for stock in arr_stock:
          if where(stock, name, username, cursor, newprice, plusminus):
            break
   # cursor.execute("SELECT username, email FROM userdata")


@app.route('/notify', methods=['GET','POST'])
@login_required
def return_notify_page():

   

   #parse_information("APPL", 170, 10)

   if request.method == 'POST':
      to = request.form["newemail"]
      email_message = ""

   return render_template('notify.html')
   

@app.route('/discover')
@login_required
def return_discover_page():
   return render_template('discover.html')

@app.route('/logout')
@login_required
def logout():
   logout_user()
   return render_template('LoginPage.html')

@app.route('/follow')
@login_required
def follow():
   return(path_calls.follow())


@app.route('/find-stock', methods=["POST"])
#@login_required
def return_discover_template_page():
   # Add searched stock to the session
   session['searched-stock'] = str.upper(request.form.get('stock'))
   return(path_calls.return_discover_template_page())
   
@app.route('/442')
def return_442_page():
   time.sleep(3)
   return render_template('442.html')



# hlb79LxeLF55X2SoJI0wA3UJSrpuB5ML89Ap8lK7
@app.route('/support')
def return_support_page():
    table_head = "<tr id = 'joe'><div class = 'na'><th>Stock Name</th><th>Stock Price</th><th>Loss / Gain</th></div></tr>"
    ###########------------------------------##################################
    #retreive from a DB (auto build)
    user_stock_list=["AAPL","NVDA","GOOG","GME"]
    prices = []
    for i in range(len(user_stock_list)):
        cur = path_calls.obtain_price(user_stock_list[i])
        sanitized = path_calls.sanitize(cur)
        prices.insert(len(prices), sanitized)
    for i in range(len(user_stock_list)):
        s_name = user_stock_list[i]
        s_price = prices[i]
        txt1 = "<tr><td>{stock_name}</td><td>{stock_price}</td><td>{to_decide}</td></tr>".format(stock_name = s_name ,stock_price = s_price, to_decide = 1)
        table_head += txt1
    return render_template('support.html', generate_table=table_head)


# test
@app.route('/test_login')
@login_required
def test_login():
   return ("You are logged in!")

@app.route('/db_test3')
def test_db3():
   username = ["test1"]
   mycursor = mydb.cursor()
   sql = "SELECT * FROM userdata WHERE username = %s"
   mycursor.execute(sql, username)
   myresult = mycursor.fetchall()

   if myresult:
      print("Something",myresult[0][2])
   else:
      print("nothing!")

   for x in myresult :
      print(x)
   return "view terminal to view databases"


@app.route('/db_view_users')
def try_db_connect2():
   cursor = mydb.cursor()
   cursor.execute("SELECT * FROM userdata")
   myresult = cursor.fetchall()

   for x in myresult :
      print(x)
   return "view terminal to view databases"

@app.route('/db_test')
def try_db_connect():

   cursor = mydb.cursor()

   sql = "DROP TABLE userdata"

   cursor.execute(sql)

   cursor.execute(
      "CREATE TABLE userdata (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), email VARCHAR(255),password VARCHAR(255),salt VARCHAR(255),is_active INT)")

   sql = "INSERT INTO userdata (username, email,password,salt,is_active) VALUES (%s, %s, %s, %s, %s)"
   val = ("test1", "email1", "pass1", "salt1", 0)
   cursor.execute(sql, val)
   mydb.commit()

   cursor.execute("SELECT * FROM userdata")
   myresult = cursor.fetchall()

   for x in myresult :
      print(x)
   return "view terminal to view databases"

@app.route('/get_news')
def get_news():
   news = path_calls.parse_xml()
   return news

@login_manager.user_loader
def user_loader(user_id):
   print("TEST?")
   print(path_calls.online_users)
   value = int(user_id)
   for x in path_calls.online_users :
      if x.id == value:
         print(x)
         return x
   print("not found")
   return DS.User()

if __name__ == '__main__':
   app.run()