import app

class Account(UserMixin, app.database.Model):
    username = app.database.Column(app.database.String(40), unique=True, primary_key=True)
    email = app.database.Column(app.database.String(40), unique=True)
    password = app.database.Column(app.database.String(50))
    salt = app.database.Column(app.database.String(100))