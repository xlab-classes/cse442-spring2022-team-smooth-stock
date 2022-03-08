from flask import Flask, request
from flask import render_template
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

import bcrypt


app = Flask(__name__)
database = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY']   = "tempkey123321"
database.init_app(app)


class Account(UserMixin, database.Model):
    username = database.Column(database.String(40), unique=True, primary_key=True)
    email = database.Column(database.String(40), unique=True)
    password = database.Column(database.String(50))
    salt = database.Column(database.String(100))


@app.route('/')
def home():
    return render_template("LandingPage.html")
def login():
    return render_template("LandingPage.html")


@app.route('/create_account',methods =["GET", "POST"])
def create_account():
    if request.method == "GET": #get request for html
        return render_template("CreateAccount.html")
    elif request.method == "POST":  #post requst for form
        username    = request.form.get("username")
        password    = request.form.get("password")
        email       = request.form.get("email")


        errorlist = ""
        if len(username) < 4:
            errorlist += "Error, username too short.\n"
        if len(password) < 8:
            errorlist += "Error, password too short.\n"
        if not any(x.isupper() for x in password):
            errorlist += "Error, no uppercase characters.\n"
        if not any(x.islower() for x in password):
            errorlist += "Error, no uppercase characters.\n"


        user = Account.query.filter_by(email=email).first()
        name = Account.query.filter_by(username=username).first()

        if user or name:
            errorlist += "Error, username or email already used"  #already have email or name we return

        if errorlist != "":
            return errorlist

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hash(password,salt)

        new_account = Account(username=username,email=email,password= hashed_password, salt =salt)


#

if __name__ == '__main__':
    app.run()




