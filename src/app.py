from re import L
from flask import Flask, render_template, request, session,url_for, redirect
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from mysql.connector import connect, Error
from flask_mail import Mail, Message
import mysql.connector
import os
import requests
import json
import smtplib
import time
# import io
# import discord
# from discord import Webhook, RequestsWebhookAdapter



t_dir = os.path.abspath('../html')
app = Flask(__name__, template_folder=t_dir)

##Temp database code for SQLalchemy, will need to be changed later for the server SQL

app.config['SECRET_KEY']   = "tempkey123321"


login_manager = LoginManager()
login_manager.login_view = 'login_needed'
login_manager.init_app(app)

#create mail object
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'SmoothStocksApp@gmail.com'
app.config['MAIL_PASSWORD'] = 'Twisted7Seven7'
app.config['MAIL_DEFAULT_SENDER'] = 'SmoothStocksApp@gmail.com'

mail = Mail(app)


mydb = mysql.connector.connect(
   host="oceanus.cse.buffalo.edu",
   user="kptodd",
   password="50318271",
   database="cse442_2022_spring_team_q_db"
)


import data_structures as DS
import path_calls
import email_path

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

def obtain(ticker):

    url = "https://yfapi.net/v6/finance/quote"
    query_string_msg = ticker + ",EURUSD=X"
    querystring = {"symbols": ""}
    querystring["symbols"] = query_string_msg
    headers = {
        'x-api-key': "hlb79LxeLF55X2SoJI0wA3UJSrpuB5ML89Ap8lK7"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response_as_bit_string = response.content
    res_utf = response_as_bit_string.decode('utf8')
    res_utf = res_utf.replace("askSize", "aakSize")

    #build the price of the stock
    ask = "ask"
    idx_ask = res_utf.find(ask)
    build_price = ""
    counter = idx_ask
    while(res_utf[counter:counter+1] != ","):
        build_price += res_utf[counter:counter+1]
        counter+=1
    

    # "regularMarketOpen":170.62
    idx_regular_market_open = res_utf.find("regularMarketOpen")
    build_open_market_price = ""
    counter1 = idx_regular_market_open
    while(res_utf[counter1:counter1+1]!= ","):
        build_open_market_price += res_utf[counter1:counter1+1]
        counter1+=1
    

    #buildthe display name
    idx_display_name = res_utf.find("displayName")
    build_display_name = ""
    counter2 = idx_display_name
    while(res_utf[counter2:counter2+1]!= ","):
        build_display_name+= res_utf[counter2:counter2+1]
        counter2+=1
  

    temp = build_price.split(":")
    price = temp[1]
    temp1 = build_open_market_price.split(":")
    open = temp1[1]
    temp2 = build_display_name.split(":")
    name = temp2[1]
    namefinal = name.replace('"', "")
  

    ret = []
    ret.insert(0, namefinal)
    ret.insert(1, price)


    #calculate price change from opening price to current price
    i_price = float(price)
    i_open = float(open)
    numerator = i_price - i_open
    res = (numerator)/i_open
    res1 = res*100
    res2 = str(res1)
    res3 = res2[0:6]
    res4 = res3 + "%"
 
    ret.insert(2, res4)

    #res4 is the percent change, #namefinal is the final name, #price is the current price of the stock

    return ret

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
            #discord_notity(stock+" price change!\n"+"New price: "+str(newprice)+"\n"+"Change By: "+str(plusminus))
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


def discord_notity(message):
   url = "https://discord.com/api/webhooks/950491418491752448/ZKjXE4laBmFGZxbls5cpZhZ3lbqiO8DXR6S9UweEQ_uowDXeh2kBmnflT9nQh6sJq47K"
   #webhook = discord.SyncWebhook.from_url(url)
   #webhook.send(message)


@app.route('/notify', methods=['GET','POST'])
@login_required
def return_notify_page():

   parse_information("APPL", 170, 10)

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

    # Get current stock from session
    current_stock = session.get('searched-stock')
    print("current_stock ->", current_stock)

    # Connect to database
    mydb = mysql.connector.connect(
        host="oceanus.cse.buffalo.edu",
        user="mdlaszlo",
        password="50265202",
        database="cse442_2022_spring_team_q_db"
    )

    # Create cursor
    cursor = mydb.cursor()

    # Disable Foreign Key Checks
    sql = "SET FOREIGN_KEY_CHECKS=0"
    cursor.execute(sql)

    # Get the current user from the session
    current_user = session.get('username')
    print("current_user = ", current_user)

    # Fetch current_user's record from saved_stocks Tabke
    sql = "SELECT stocks FROM saved_stocks WHERE username = %s"
    cursor.execute(sql, [current_user])
    record = cursor.fetchone()
    print("stocks followed ->", record[0])
    stocks_followed = record[0]


    ret_list = []
    for i in range(len(stocks_followed)):
        cur = obtain(stocks_followed[i])
        ret_list.insert(len(ret_list), cur)
    for i in range(len(ret_list)):
        s_name = ret_list[i][0]
        s_price = ret_list[i][1]
        percent = ret_list[i][2]
        txt1 = "<tr><td>{stock_name}</td><td>{stock_price}</td><td>{to_decide}</td></tr>".format(stock_name= s_name,  stock_price= s_price, to_decide= percent)
        table_head += txt1
    return render_template('support.html', generate_table=table_head)


@app.route('/tech1')
def return_tech1_page():
    table_head = "<tr id = 'joe'><div class = 'na'><th>Stock Name</th><th>Stock Price</th><th>Loss / Gain</th></div></tr>"

    stocks_followed = ["GOOG", "AAPL", "NVDA", "SWCH"]
    ret_list = []
    for i in range(len(stocks_followed)):
        cur = obtain(stocks_followed[i])
        ret_list.insert(len(ret_list), cur)
    for i in range(len(ret_list)):
        s_name = ret_list[i][0]
        s_price = ret_list[i][1]
        percent = ret_list[i][2]
        txt1 = "<tr><td>{stock_name}</td><td>{stock_price}</td><td>{to_decide}</td></tr>".format(stock_name=s_name,
                                                                                                 stock_price=s_price,
                                                                                                 to_decide=percent)
        table_head += txt1
    return render_template('tech1.html', generate_table=table_head)


@app.route('/energy1')
def return_energy1_page():
    table_head = "<tr id = 'joe'><div class = 'na'><th>Stock Name</th><th>Stock Price</th><th>Loss / Gain</th></div></tr>"

    stocks_followed = ["MPC", "DINO", "FANG", "CNP"]
    ret_list = []
    for i in range(len(stocks_followed)):
        cur = obtain(stocks_followed[i])
        ret_list.insert(len(ret_list), cur)
    for i in range(len(ret_list)):
        s_name = ret_list[i][0]
        s_price = ret_list[i][1]
        percent = ret_list[i][2]
        txt1 = "<tr><td>{stock_name}</td><td>{stock_price}</td><td>{to_decide}</td></tr>".format(stock_name=s_name,
                                                                                                 stock_price=s_price,
                                                                                                 to_decide=percent)
        table_head += txt1
    return render_template('energy1.html', generate_table=table_head)



@app.route('/telecom1')
def return_telecom1_page():
    table_head = "<tr id = 'joe'><div class = 'na'><th>Stock Name</th><th>Stock Price</th><th>Loss / Gain</th></div></tr>"

    stocks_followed = ["T", "VZ", "TMUS", "TEF"]
    ret_list = []
    for i in range(len(stocks_followed)):
        cur = obtain(stocks_followed[i])
        ret_list.insert(len(ret_list), cur)
    for i in range(len(ret_list)):
        s_name = ret_list[i][0]
        s_price = ret_list[i][1]
        percent = ret_list[i][2]
        txt1 = "<tr><td>{stock_name}</td><td>{stock_price}</td><td>{to_decide}</td></tr>".format(stock_name=s_name,
                                                                                                 stock_price=s_price,
                                                                                                 to_decide=percent)
        table_head += txt1
    return render_template('telecom1.html', generate_table=table_head)

#new path for confirming a email token
@app.route('/reset/<token>', methods=["GET", "POST"])
def token_reset(token):
    return email_path.token_reset(token)



@app.route('/reset', methods=["GET", "POST"])
def reset_email():
    return email_path.reset_email()


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
