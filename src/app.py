from flask import Flask, render_template, request
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import connect, Error
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

@app.route('/find-stock', methods=["POST"])
def return_discover_template_page():

   # Trying to remove updated_discover_template file if it exists
   if os.path.exists('../html/updated_discover_template.html'):
      print("Path exists. Removing file...")
      os.remove('../html/updated_discover_template.html')
   else:
      print("Path does not exist")

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

   # Read in find_stock.html
   file = open('../html/discover_template.html')
   file_data = file.read()

   # Close discover_template.html as we only need to manipulate discover_template.html now
   file.close()

   # Replace search bar text with the company User searched
   file_data = file_data.replace("Enter name of company stock to search...", dict.get('quoteResponse').get('result')[0].get('displayName'))

   # Replace Stock Name with actual name of stock User searched
   file_data = file_data.replace("Stock Name", dict.get('quoteResponse').get('result')[0].get('symbol'))

   # Replace Company with actual name of company User searched
   file_data = file_data.replace("Company", dict.get('quoteResponse').get('result')[0].get('displayName'))

   # Replace Current Stock Price with actual value
   file_data = file_data.replace("Current Stock Price", str(dict.get('quoteResponse').get('result')[0].get('regularMarketPrice')))

   # Replace Current plus/minus with actual value
   file_data = file_data.replace("Current plus/minus", str(dict.get('quoteResponse').get('result')[0].get('regularMarketChangePercent')))

   # Replace 'Stock History (as a visual)' with:
   # 1. 52-Week Range
   # 2. 50 day average
   # 3. 200 day average
   # 4. epsCurrentYear
   # 5. priceEpsCurrentYear
   # 6. averageAnalystRating
   new_string = ""
   new_string += "52-Week Range: " + dict.get('quoteResponse').get('result')[0].get('fiftyTwoWeekRange') + "<br>"
   new_string += "50 Day average: " + str(dict.get('quoteResponse').get('result')[0].get('fiftyDayAverage')) + "<br>"
   new_string += " 200 Day Average: " + str(dict.get('quoteResponse').get('result')[0].get('twoHundredDayAverage')) + "<br>"
   new_string += " EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('epsCurrentYear')) + "<br>"
   new_string += " Price EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('priceEpsCurrentYear')) + "<br>"
   new_string += " Average Analyst Rating: " + dict.get('quoteResponse').get('result')[0].get('averageAnalystRating') 
   file_data = file_data.replace("Stock History (as a visual)", new_string)

   # Write file data to output file
   output_file = open("../html/updated_discover_template.html", "w")
   output_file.write(file_data)
   output_file.close()

   # Return html page to be rendered
   return render_template('updated_discover_template.html')

@app.route('/442')
def return_442_page():
   return render_template('442.html')

@app.route('/CreateAccount')
def return_CA_page():
   return render_template('CreateAccount.html')


@app.route('/test_login')
@login_required
def test_login():
   return ("You are logged in!")

@app.route('/db_test')
def try_db_connect():
   databases = ""
   try:
    with connect(
        host="oceanus.cse.buffalo.edu",
        user="jakeheid",
        password="50271130",
    ) as connection:
        db_query = "SHOW DATABASES;"
        with connection.cursor() as cursor:
            cursor.execute(db_query)
            for db in cursor:
               print(db)
               

   except Error as e:
      print(e)
   return "view terminal to view databases"

@login_manager.user_loader
def user_loader(user_id):
   return DS.Account.query.get(int(user_id))

if __name__ == '__main__':
   app.run()