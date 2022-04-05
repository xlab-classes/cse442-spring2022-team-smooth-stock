from flask_login import LoginManager, UserMixin
import app

class Account(UserMixin, app.database.Model):
    id = app.database.Column(app.database.Integer, primary_key=True)
    username = app.database.Column(app.database.String(40), unique=True)
    email = app.database.Column(app.database.String(40), unique=True)
    password = app.database.Column(app.database.String(50))
    salt = app.database.Column(app.database.String(100))

