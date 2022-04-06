from flask import Flask, render_template, request, session
from flask_login import login_user
import bcrypt
from app import DS
from app import database
from app import mydb
import json

online_users = []


def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    if request.form.get("Remember me"):
        remember = True
    else:
        remember = False
    errorlist = ""

    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE username = %s"
    mycursor.execute(sql,[username])
    user = mycursor.fetchone()


    if not user :
        errorlist += "User not found.\n"
        return render_template('LoginPage.html', error = errorlist)
    else :
        salt = user[4] #4 is salt
        salt = salt.encode()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        realpassword = user[3].encode() #3 is password

        if realpassword == hashed_password :

            newlogin = DS.User()
            newlogin.id=user[0]
            newlogin.is_authenticated=True
            newlogin.is_active=True
            online_users.append(newlogin)
            print(login_user(newlogin)) #set cookies to show user is logged in
            return render_template('LoginPage.html', error = "You're logged in!")
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

    salt = bcrypt.gensalt()
    print("Salt",salt)
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    print("Hashed_pass",hashed_password)

    salt = salt.decode()#encode the salt for putting into sql
    hashed_password = hashed_password.decode()

    sql = "INSERT INTO userdata (username, email,password,salt) VALUES (%s, %s, %s, %s)"
    val = (username, email, hashed_password, salt)
    mycursor.execute(sql, val)
    mydb.commit()

    errorlist = "Account created!"
    return render_template('CreateAccount.html', error = errorlist)

def parse_xml():
        with open("a.xml", "r") as file:
                content = file.readlines()
                content = "".join(content)
                bs_content = BeautifulSoup(content, "lxml")
                items = bs_content.find_all("item")
                titles = []
                links = []
                dates = []

                for i in items:
                        title = i.find("title").text
                        titles.append(title)
                        link = i.contents[2]
                        links.append(link)
                d = list(zip(titles, links))
        return json.dumps(d)