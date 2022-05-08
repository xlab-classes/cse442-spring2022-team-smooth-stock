from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import login_user,logout_user
import hashlib
from app import DS
from app import mydb, os
from bs4 import BeautifulSoup
import requests
import mysql.connector
import json
import smtplib
#from discord import SyncWebhook
import xml.etree.ElementTree as ET


online_users = []


def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    errorlist = ""

    mydb.reconnect() #reconnection to server
    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE username = %s"
    mycursor.execute(sql,[username])
    user = mycursor.fetchone()


    if not user :
        errorlist += "User not found.\n"
        return render_template('LoginPage.html', error = errorlist)
    else :
        salt = user[4].encode('latin1') #4 is salt
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000).decode('latin1')
        realpassword = user[3] #3 is password

        if realpassword == hashed_password :

            newlogin = DS.User()
            newlogin.id=user[0]
            newlogin.is_authenticated=True
            newlogin.is_active=True
            online_users.append(newlogin)
            print(login_user(newlogin)) #set cookies to show user is logged in

            # Store User username to session
            session['username'] = username

            return render_template('LandingPage.html')
        else :
            return render_template('LoginPage.html', error = "Wrong password")


def create_account(request):
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    errorlist = ""
    if len(username) < 4 :
        errorlist += ", username too short"
    if len(password) < 8 :
        errorlist += ", password too short"
    if not any(x.isupper() for x in password) :
        errorlist += ", no uppercase characters"
    if not any(x.islower() for x in password) :
        errorlist += ", no lowercase characters"

    mydb.reconnect()  # reconnection to server
    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE username = %s"
    mycursor.execute(sql,[username])
    user = mycursor.fetchone()

    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE email = %s"
    mycursor.execute(sql,[email])
    mail = mycursor.fetchone()



    if user or mail :
        errorlist += ", username or email already used"  # already have email or name we return

    if errorlist != "" :
        errorlist = "Error" + errorlist + "."
        return render_template('CreateAccount.html', error = errorlist)

    salt = os.urandom(32)
    print("Salt",salt)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000).decode('latin1')
    print("Hashed_pass",hashed_password)


    # Insert User account information into userdata Table
    sql = "INSERT INTO userdata (username, email,password,salt) VALUES (%s, %s, %s, %s)"
    val = (username, email, hashed_password, salt.decode('latin1'))
    mycursor.execute(sql, val)
    mydb.commit()

    # Insert User account information into saved_stocks Table
    sql = "SELECT * FROM userdata WHERE username = %s"
    mycursor.execute(sql, [username])
    user_id = mycursor.fetchone()
    print("user_id =", user_id[0])

    sql = "SET FOREIGN_KEY_CHECKS=0"
    mycursor.execute(sql)

    sql = "INSERT INTO saved_stocks (userID, username, stocks) VALUES (%s, %s, %s)"
    val = (user_id[0], user_id[1], "")
    mycursor.execute(sql, val)
    mydb.commit()

    sql = "SET FOREIGN_KEY_CHECKS=1"
    mycursor.execute(sql)

    errorlist = "Account created!"
    return render_template('LoginPage.html', error = errorlist)

def delete_account(request):
    username = session.get('username')
    delete = request.form.get("delete")
    password = request.form.get("password")
    errorlist = ""

    if delete != "DELETE":
        errorlist += "\"DELETE\" not entered correctly!\n"

    mydb.reconnect()  # reconnection to server
    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE username = %s"
    mycursor.execute(sql, [username])
    user = mycursor.fetchone()

    salt = user[4].encode('latin1')  # 4 is salt
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000).decode('latin1')
    realpassword = user[3]  # 3 is password

    if realpassword != hashed_password:
        errorlist += "Error, wrong password."
        return render_template("delete_account.html", error=errorlist)
    else:

        sql = "DELETE FROM userdata WHERE username = %s"
        mycursor.execute(sql, [username])
        sql = "DELETE FROM saved_stocks WHERE username = %s"
        mycursor.execute(sql,[username])
        mydb.commit()
        logout_user()
        return render_template('LoginPage.html', error="Account of "+username+" has been deleted.")

def save_yahoo_xml(url):
        response = requests.get(url)
        with open("a.xml", 'wb') as f:
                f.write(response.content)

def parse_xml():
        save_yahoo_xml("https://finance.yahoo.com/rss/")
        mytree = ET.parse('a.xml')
        myroot = mytree.getroot()
        links = []
        titles = []
        sources = []
        for link in myroot.iter('link'):
            if link.text != "https://finance.yahoo.com/":
                links.append(link.text)
        for title in myroot.iter('title'):
            if "Yahoo Finance" not in title.text:
                titles.append(title.text)
        for source in myroot.iter('source'):
            sources.append(source.text)
        zipped = list(zip(titles, links, sources))
        zipped.append(("Why Google Is the Safest Nasdaq Stock to Buy", "https://www.nasdaq.com/articles/why-google-is-the-safest-nasdaq-stock-to-buy", "nasdaq"))
        zipped.append(("Microsoft Gets Antitrust Complaints From Aruba, Danish Firms Over Cloud", "https://www.msn.com/en-us/money/other/microsoft-gets-antitrust-complaints-from-aruba-danish-firms-over-cloud/ar-AAWaUlX?ocid=BingNewsSearch", "msn"))
        zipped.append(("Apple mixed reality glasses release pushed to 2023, report claims", "https://www.msn.com/en-us/news/technology/apple-mixed-reality-glasses-release-pushed-to-2023-report-claims/ar-AAWaNO7?ocid=BingNewsSearch", "msn"))
        return zipped

# follow function. Connects to the database and updates the current User's
# list of followed stocks
def follow():

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

    # Fetch current_user's record from saved_stocks Tabke
    sql = "SELECT stocks FROM saved_stocks WHERE username = %s"
    cursor.execute(sql, [current_user])
    record = cursor.fetchone()

    if (record != None) :
        print("stocks followed ->", record[0])
        stocks_followed = record[0]
    else :
        stocks_followed = ""

    # IF stocks_followed is an empty string
    if(stocks_followed == ""):

        # Just add stock to stocks_followed string
        stocks_followed = stocks_followed + current_stock

    else:

        # Split by comma to get indvidual stocks followed by User
        stocks = stocks_followed.split(", ")

        # Initialize new_stock to True
        new_stock = True

        # For each entry in stocks
        for stock in stocks:

            # Ensure stock is in all caps
            stock = str.upper(stock)

            # If stock equals current_stock
            if(stock == current_stock):

                # Set new_stock to False
                new_stock = False
       
        # If new_stock is True
        if(new_stock):
            
            # Add , then stock to stocks_followed string
            stocks_followed = stocks_followed + ", " + current_stock

        # Else new_stock is False, User was already following this stock
        else:

            # Remove current_stock from stocks_followed
            stocks_followed = stocks_followed.replace((current_stock + ", "), "", 1)
            stocks_followed = stocks_followed.replace((", " + current_stock), "", 1)
            stocks_followed = stocks_followed.replace(current_stock, "", 1)

    # Update saved_stock Table for User 
    sql = "UPDATE saved_stocks SET stocks = %s WHERE username = %s"
    val = (stocks_followed, current_user)
    cursor.execute(sql, val)
    mydb.commit()

    # Print saved_stocks information
    cursor.execute("SELECT * FROM saved_stocks")
    myresult = cursor.fetchall()
    print(myresult)

    # Re-enable Foreign Key Checks 
    sql = "SET FOREIGN_KEY_CHECKS=1"
    cursor.execute(sql)

    # Render initial discover page (for now)
    return return_discover_template_page(current_stock)

#return_discover_template_page.
def return_discover_template_page(symbol):

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
    company_symbol = symbol

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

    # Initialize all variables to be not found
    stock_symbol = "Stock Symbol Not Found"
    company = "Company Not Found"
    current_stock_price = "Current Stock Price Not Found"
    current_plus_minus = "Current Plus/Minus Not Found"
    price_history = "Price History Not Found"
    fifty_two_week_range = "52-Week Range Not Found"
    fifty_day_average = "50-Day Average Not Found"
    two_hundred_day_average = "200-Day Average Not Found"
    eps_current_year = "EPS Current Year Not Found"
    price_eps_current_year = "Price EPS Current Year Not Found"
    average_analyst_rating = "Average Analyst Rating Not Found"

    # Reinitialiaze any variables that are not None
    if(dict.get('quoteResponse').get('result')[0].get('symbol') is not None):
        stock_symbol = dict.get('quoteResponse').get('result')[0].get('symbol')

    if(dict.get('quoteResponse').get('result')[0].get('displayName') is not None):
        company = dict.get('quoteResponse').get('result')[0].get('displayName')
        price_history = company + "'s Price History"

    if(str(dict.get('quoteResponse').get('result')[0].get('regularMarketPrice')) is not None):
        current_stock_price = str(dict.get('quoteResponse').get('result')[0].get('regularMarketPrice'))

    if(str(dict.get('quoteResponse').get('result')[0].get('regularMarketChangePercent')) is not None):
        current_plus_minus = str(dict.get('quoteResponse').get('result')[0].get('regularMarketChangePercent'))

    if(dict.get('quoteResponse').get('result')[0].get('fiftyTwoWeekRange') is not None):
        fifty_two_week_range = "52-Week Range: " + dict.get('quoteResponse').get('result')[0].get('fiftyTwoWeekRange')

    if(str(dict.get('quoteResponse').get('result')[0].get('fiftyDayAverage')) is not None):
        fifty_day_average = "50 Day average: " + str(dict.get('quoteResponse').get('result')[0].get('fiftyDayAverage'))

    if(str(dict.get('quoteResponse').get('result')[0].get('twoHundredDayAverage')) is not None):
        two_hundred_day_average = " 200 Day Average: " + str(dict.get('quoteResponse').get('result')[0].get('twoHundredDayAverage'))

    if(str(dict.get('quoteResponse').get('result')[0].get('epsCurrentYear')) is not None):
        eps_current_year = " EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('epsCurrentYear'))

    if(str(dict.get('quoteResponse').get('result')[0].get('priceEpsCurrentYear')) is not None):
        price_eps_current_year = " Price EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('priceEpsCurrentYear'))

    if(dict.get('quoteResponse').get('result')[0].get('averageAnalystRating') is not None):
        average_analyst_rating = " Average Analyst Rating: " + dict.get('quoteResponse').get('result')[0].get('averageAnalystRating')


    """
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
    """

    """ Check if User is already following the stock they searched """
    # Connect to database
    mydb = mysql.connector.connect(
        host="oceanus.cse.buffalo.edu",
        user="mdlaszlo",
        password="50265202",
        database="cse442_2022_spring_team_q_db"
    )

    # Create cursor
    cursor = mydb.cursor()

    # Disable Foreign Key Checks (for now)
    sql = "SET FOREIGN_KEY_CHECKS=0"
    cursor.execute(sql)

    # Get the current user from the session
    current_user = session.get('username')

    # Fetch current_user's record from saved_stocks Tabke
    sql = "SELECT stocks FROM saved_stocks WHERE username = %s"
    cursor.execute(sql, [current_user])
    record = cursor.fetchone()
    if(record != None):
        print("stocks followed ->", record[0])
        stocks_followed = record[0]
    else:
        stocks_followed = ""
    # If company_symbol is in stocks_followed
    if(company_symbol in stocks_followed):

        # Set button text to Unfollow Stock
        button_text = "Unfollow Stock"

    else:

        # Set button text to Follow Stock
        button_text = "Follow Stock"

    # Re-enable Foreign Key Checks 
    sql = "SET FOREIGN_KEY_CHECKS=1"
    cursor.execute(sql)

    news_articles = parse_xml()
    filtered_news = []
    for title, link, src in news_articles:
        lower = title.lower()
        if symbol in lower or ticker_to_stock_name(symbol.upper()) in lower:
            filtered_news.append((title, link))
    print("------FILTERED NEWS------")
    print(filtered_news)
    # Return html page to be rendered
    return render_template('discover_template.html', Stock_Name=stock_symbol, Company=company, Current_Stock_Price=current_stock_price, Current_plus_minus=current_plus_minus, Price_History=price_history, Fifty_Two_Week_Range=fifty_two_week_range, Fifty_Day_Average=fifty_day_average, Two_Hundred_Day_Average=two_hundred_day_average, EPS_Current_Year=eps_current_year, Price_EPS_Current_Year=price_eps_current_year, Average_Analyst_Rating=average_analyst_rating, Follow_Button=button_text, news=filtered_news)

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


def get_user_stocks(username):
    db = mysql.connector.connect(
        host="oceanus.cse.buffalo.edu",
        user="jakeheid",
        password="50271130",
        database="cse442_2022_spring_team_q_db"
    )
    cursor = db.cursor()
    saved_stocks_query = "SELECT stocks FROM saved_stocks WHERE username = %s"
    saved_stocks_params = [username]
    cursor.execute(saved_stocks_query, saved_stocks_params)

    try:
        result = cursor.fetchone()[0]
        stocks = str.split(result, ', ')
        if len(stocks) == 1 and stocks[0] == "": #empty column returns [''] which will lead to every single news article included
            return []
        else:
            return stocks
    except:
        return []

def ticker_to_stock_name(ticker):
    ticker = ticker.lower()
    if ticker == "goog":
        return "google"
    elif ticker == "aapl":
        return "apple"
    elif ticker == "msft":
        return "microsoft"
    elif ticker == "twtr":
        return "twitter" 
    else:
        return "not implemented"


