from flask import Flask, render_template, request
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import connect, Error
import os
import requests
import time



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
def sanitize(str):
    count = 0
    a = str.replace(",", "")
    idx = a.find(".")
    for i in range(idx, len(a) - 1):
        count += 1
    if count < 2 :
        store = a + "0"
        return store
    return a
def obtain_price(ticker):
    url = "https://yfapi.net/v6/finance/quote"
    query_string_msg = ticker + ",EURUSD=X"
    querystring = {"symbols": ""}
    querystring["symbols"] = query_string_msg
    headers = {
        'x-api-key': "hlb79LxeLF55X2SoJI0wA3UJSrpuB5ML89Ap8lK7"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response_as_bit_string = response.content
    int = response_as_bit_string.find(b'ask')
    build = b''
    for i in range(int, int + 11):
        build += response_as_bit_string[i:i + 1]

    str_build = str(build)
    price_str = str_build[7:len(str_build) - 1]
    return price_str


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

@app.route('/442')
def return_442_page():
   time.sleep(3)
   return render_template('442.html')

@app.route('/CreateAccount')
def return_CA_page():
   return render_template('CreateAccount.html')


# hlb79LxeLF55X2SoJI0wA3UJSrpuB5ML89Ap8lK7
@app.route('/support')
def return_support_page():
    table_head = "<tr id = 'joe'><div class = 'na'><th>Stock Name</th><th>Stock Price</th><th>Loss / Gain</th></div></tr>"
    ###########------------------------------##################################
    #retreive from a DB (auto build)
    user_stock_list=["AAPL","NVDA","GOOG","GME"]
    prices = []
    for i in range(len(user_stock_list)):
        cur = obtain_price(user_stock_list[i])
        sanitized = sanitize(cur)
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