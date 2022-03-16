from flask import Flask, render_template, request
from flask_login import login_user
import bcrypt
from app import DS
from app import database

def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    if request.form.get("Remember me"):
        remember = True
    else:
        remember = False

    errorlist = ""
    user = DS.Account.query.filter_by(username=username).first()

    if not user :
        errorlist += "User not found.\n"
        return render_template('LoginPage.html', error = errorlist)
    else :
        salt = user.salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        realpassword = user.password

        if realpassword == hashed_password :
            login_user(user,remember=remember) #set cookies to show user is logged in
            return render_template('LoginPage.html', error = "You're logged in!")
        else :
            return render_template('LoginPage.html', error = errorlist)


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

    user = DS.Account.query.filter_by(email=email).first()
    name = DS.Account.query.filter_by(username=username).first()

    if user or name :
        errorlist += ", username or email already used"  # already have email or name we return

    if errorlist != "" :
        errorlist = "Error" + errorlist + "."
        return render_template('CreateAccount.html', error = errorlist)

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    new_account = DS.Account(username=username, email=email, password=hashed_password, salt=salt)

    database.session.add(new_account)
    database.session.commit()

    errorlist = "Account created!"
    return render_template('CreateAccount.html', error = errorlist)