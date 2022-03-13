from flask import Flask, render_template, request
import bcrypt


def login(request):
    username = request.form.get("username")
    password = request.form.get("password")

    errorlist = ""

    user = Account.query.filter_by(username=username).first()

    if not user :
        errorlist += "User not found.\n"
        return errorlist
    else :
        salt = user.salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        realpassword = user.password

        if realpassword == hashed_password :
            return "User logged in!"
        else :
            return "Wrong password."

def create_account(request):
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    errorlist = ""
    if len(username) < 4 :
        errorlist += "Error, username too short.\n"
    if len(password) < 8 :
        errorlist += "Error, password too short.\n"
    if not any(x.isupper() for x in password) :
        errorlist += "Error, no uppercase characters.\n"
    if not any(x.islower() for x in password) :
        errorlist += "Error, no uppercase characters.\n"

    user = Account.query.filter_by(email=email).first()
    name = Account.query.filter_by(username=username).first()

    if user or name :
        errorlist += "Error, username or email already used"  # already have email or name we return

    if errorlist != "" :
        return errorlist

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    new_account = Account(username=username, email=email, password=hashed_password, salt=salt)

    database.session.add(new_account)
    database.session.commit()

    return ("Account created!")