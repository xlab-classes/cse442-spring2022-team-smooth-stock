from flask import Flask, render_template, request, session
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import connect, Error
import mysql.connector
import os
import requests
import json


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
@login_required
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
@login_required
def return_notify_page():
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

@app.route('/find-stock', methods=["POST"])
@login_required
def return_discover_template_page():

   """
   Variables to be obtained from Yahoo Finance API to be displayed on web page:
   1. Price History
   2. Fifty_Two_Week_Range
   3. Fifty_Day_Average
   4. Two_Hundred_Day_Average
   5. EPS_Current_Year
   6. Price_EPS_Current_Year
   7. Average_Analyst_Rating
   8. Stock_Name -> Symbol of the stock being searched
   9. Company
   10. Current_Stock_Price
   11. Current_plus_minus
   """

   # Get the company sybmol user is looking for
   company_symbol = request.form.get('stock')
   print(company_symbol)

   # Create url for Yahoo Finace API
   url = "https://yfapi.net/v6/finance/quote"

   # Create querystring to find company stock info
   querystring = {"symbols":company_symbol}
   
   # Create headers dictionary with API Key
   headers = {
      'x-api-key': "REiSqBThOa9z6bIgDGJ2l4S92jMKXl8O1yRsROBK"
   }

   # Send request to Yahoo Finance API and store response
   response = requests.request("GET", url, headers=headers, params=querystring)

   # Load response as a dictionary
   dict = json.loads(response.text)

   # Initialize variables stated at beginning of function 
   stock_symbol = dict.get('quoteResponse').get('result')[0].get('symbol')
   company = dict.get('quoteResponse').get('result')[0].get('displayName')
   current_stock_price = str(dict.get('quoteResponse').get('result')[0].get('regularMarketPrice'))
   current_plus_minus = str(dict.get('quoteResponse').get('result')[0].get('regularMarketChangePercent'))
   price_history = company + "'s Price History"
   fifty_two_week_range = "52-Week Range: " + dict.get('quoteResponse').get('result')[0].get('fiftyTwoWeekRange')
   fifty_day_average = "50 Day average: " + str(dict.get('quoteResponse').get('result')[0].get('fiftyDayAverage'))
   two_hundred_day_average = " 200 Day Average: " + str(dict.get('quoteResponse').get('result')[0].get('twoHundredDayAverage'))
   eps_current_year = " EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('epsCurrentYear'))
   price_eps_current_year = " Price EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('priceEpsCurrentYear'))
   average_analyst_rating = " Average Analyst Rating: " + dict.get('quoteResponse').get('result')[0].get('averageAnalystRating')

   # Return html page to be rendered
   return render_template('discover_template.html', Stock_Name=stock_symbol, Company=company, Current_Stock_Price=current_stock_price, Current_plus_minus=current_plus_minus, Price_History=price_history, Fifty_Two_Week_Range=fifty_two_week_range, Fifty_Day_Average=fifty_day_average, Two_Hundred_Day_Average=two_hundred_day_average, EPS_Current_Year=eps_current_year, Price_EPS_Current_Year=price_eps_current_year, Average_Analyst_Rating=average_analyst_rating)

@app.route('/442')
def return_442_page():
   return render_template('442.html')


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