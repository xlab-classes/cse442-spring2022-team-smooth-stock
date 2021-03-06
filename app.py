from concurrent.futures import thread
from email import message
#from turtle import st
from flask import Flask, render_template, request, session
from flask_login import LoginManager, login_required, logout_user
from mysql.connector import connect
from flask_mail import Mail
import mysql.connector
import os
import requests
import smtplib
import time
# import io
#from discord import Webhook, RequestsWebhookAdapter




t_dir = os.path.abspath('html')
app = Flask(__name__, template_folder='html')

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

@app.route('/loginpage')
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
   xml = path_calls.parse_xml()
   bing_results = []
   unique_total_sources = []
   filtered_xml = []
   username = session.get('username')
   if username == None:
      username = "fakeuser"
   user_stocks = path_calls.get_user_stocks(username)
   for stock in user_stocks:
      bing_results += path_calls.get_bing_search_results(stock)
   for title, link, source in xml:
      lower = title.lower()
      for stock in user_stocks:
         ticker = path_calls.ticker_to_stock_name(stock)
         if stock in lower or ticker in lower:
            filtered_xml.append((title, link, source))
            unique_total_sources.append(source)
   unique_total_sources = list(set(unique_total_sources))
   filtered_xml = filtered_xml + bing_results
   return render_template('news.html', title=filtered_xml, sources=unique_total_sources)

@app.route('/create_account',methods =["GET", "POST"])
def create_account() :
   if request.method == "GET" :  # get request for html
      return render_template("CreateAccount.html")
   elif request.method == "POST":  # post requst for form
      return path_calls.create_account(request)

@app.route('/delete_account',methods =["GET", "POST"])
def delete_account() :
   if request.method == "GET" :  # get request for html
      return render_template("delete_account.html")
   elif request.method == "POST":  # post requst for form
      return path_calls.delete_account(request)


@app.route('/LandingPage')
@login_required
def return_landing_page():
    current_user = session.get('username')
    return render_template('LandingPage.html',error="Logged in user: " + current_user)

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
    idx_ask = res_utf.find("ask")
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
    idx_display_name = res_utf.find("longName")
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


def sendEmailNotification(sender_to, message):
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
      print ("Something went wrong???.",ex)

   
def stock_information(username, num, email):
   mydb = mysql.connector.connect(
         host="oceanus.cse.buffalo.edu",
         user="dtan2",
         password="50278774",
         database="cse442_2022_spring_team_q_db"
      )
   cursor = mydb.cursor()
   sql = "SELECT stocks FROM saved_stocks WHERE username = %s"
   cursor.execute(sql, [username])
   stock = cursor.fetchone()

   arr_stock = (stock[0].split(', '))
   
   
   for ss in arr_stock:
      s = obtain(ss)
      price_change = (abs(float(s[2].split('%')[0])))
      if price_change>num:
         sendEmailNotification(email, ss+" price change!\n"+"New price: "+str(s[1])+"\n"+"Change By: "+str(s[2]))
         #discord_notity(stock+" price change!\n"+"New price: "+str(s[1])+"\n"+"Change By: "+str(s[2]))

         
   # cursor.execute("SELECT username, email FROM userdata")


def news_information(username, email):
   mydb = mysql.connector.connect(
         host="oceanus.cse.buffalo.edu",
         user="dtan2",
         password="50278774",
         database="cse442_2022_spring_team_q_db"
      )
   message = ""
   cursor = mydb.cursor()
   sql = "SELECT stocks FROM saved_stocks WHERE username = %s"
   cursor.execute(sql, [username])
   stock = cursor.fetchone()

   sendEmailNotification(email, message)

# def discord_notity(message):
#     url = "https://discord.com/api/webhooks/950491418491752448/ZKjXE4laBmFGZxbls5cpZhZ3lbqiO8DXR6S9UweEQ_uowDXeh2kBmnflT9nQh6sJq47K"
#     webhook = Webhook.from_url(url, adapter=RequestsWebhookAdapter()) # Initializing webhook
#     webhook.send(content=message) # Executing webhook.


#discord_notity("test")
import threading
def check_prices(user, num, count, email):
   if count < 5:
      threa = threading.Timer(60,startTimer,(user, num, count,email, ))
      threa.daemon = True
      threa.start()
   #discord_notity('NVDA'+"This is just a test. No news yet")
   #runs every hours


def startTimer(user, num, count, email):
   print(count)
   stock_information(user, num, email)
   check_prices(user, num, count+1, email)



@app.route('/notify', methods=['GET','POST'])
@login_required
def return_notify_page():
   
   current_user = session.get('username')

   mydb = mysql.connector.connect(
         host="oceanus.cse.buffalo.edu",
         user="dtan2",
         password="50278774",
         database="cse442_2022_spring_team_q_db"
      )
   mycursor = mydb.cursor()
   stocks = path_calls.get_user_stocks(current_user)


   sql = "SELECT email FROM userdata WHERE username = %s"
   mycursor.execute(sql, [current_user])
   user = mycursor.fetchone()
   percent = ""
   new_email = user[0]

   if request.method == 'POST':

      if request.form['submit_button'] == 'Notify when price change .5%':
         check_prices(current_user, .5, 0, new_email)
         percent = "Currently notifying at .5%"
      elif request.form['submit_button'] == 'Notify when price change 1%':
         check_prices(current_user, 1, 0, new_email)
         percent = "Currently notifying at 1%"
      else:
         if request.form["newemail"] != "":
            new_email = request.form["newemail"]
            mydb.reconnect()  # reconnection to server
            mycursor = mydb.cursor()
            sql = 'UPDATE userdata SET email = %s WHERE username = %s'
            val = (new_email,current_user)
            mycursor.execute(sql,val)
            mydb.commit()
      if stocks != "" or None:
        stocks = "Followed stocks: " + ", ".join(stocks) + "."
      return render_template('notify.html',name=current_user, error=stocks, curr_email=new_email, notity_percent=percent)
   else:

      if stocks != "" or None:
         stocks = "Followed stocks: " + ", ".join(stocks) + "."

      return render_template('notify.html',name=current_user,error=stocks, curr_email=user[0])
   

@app.route('/discover')
@login_required
def return_discover_page():
   return render_template('discover.html', Message="")

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
@login_required
def return_discover_template_page():
   # Add searched stock to the session
   session['searched-stock'] = str.upper(request.form.get('stock'))
   return(path_calls.return_discover_template_page(str.upper(request.form.get('stock'))))
   
@app.route('/442')
@login_required
def return_442_page():
   time.sleep(3)
   return render_template('442.html')



# hlb79LxeLF55X2SoJI0wA3UJSrpuB5ML89Ap8lK7
@app.route('/support')
def return_support_page():      
    table_head = "<tr id = 'joe'><div class = 'na'><th>Stock Name</th><th>Stock Price</th><th>Loss / Gain</th></div></tr>"    
    ret_list = []
    username = session.get('username')
    user_stocks = path_calls.get_user_stocks(username)
    stocks_followed = []
    stocks_followed = user_stocks
   
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



@app.route('/energy1')
def return_energy1_page():
    return(path_calls.return_energy1_page_template())

@app.route('/tech1')
def return_tech1_page():
    return(path_calls.return_tech1_page_template())
@app.route('/telecom1')
def return_telecom1_page():
    return(path_calls.return_telecom1_page_template())


#new path for confirming a email token
@app.route('/reset/<token>', methods=["GET", "POST"])
def token_reset(token):
    return email_path.token_reset(token)



@app.route('/reset', methods=["GET", "POST"])
def reset_email():
    return email_path.reset_email()


@app.route('/db_view_users')
def try_db_connect2():
   cursor = mydb.cursor()
   cursor.execute("SELECT * FROM userdata")
   myresult = cursor.fetchall()

   for x in myresult :
      print(x)
   return "view terminal to view databases"



@login_manager.user_loader
def user_loader(user_id):
   value = int(user_id)
   for x in path_calls.online_users :
      if x.id == value:
         print(x)
         return x
   return DS.User()



if __name__ == '__main__':
   app.run(threaded=True)
