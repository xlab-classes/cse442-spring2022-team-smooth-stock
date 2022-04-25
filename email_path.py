from flask import url_for, redirect, render_template, app, request
from flask_mail import Mail, Message
import hashlib, os
from forms import ResetEmailForm, ResetPasswordForm
from app import mydb, app, mail
from itsdangerous import URLSafeTimedSerializer
from threading import Thread






def send_reset_link(email):
    password_reset = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    password_reset_url = url_for('token_reset',token = password_reset.dumps(email, salt='password-reset-salt'),_external=True)
    html = render_template('email_reset.html',password_reset_url=password_reset_url)

    send_email('Password Reset Requested', [email], html)

def send_email_thread(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    thread = Thread(target=send_email_thread, args=[msg])
    thread.start()


def reset_email():
    form = ResetEmailForm()
    print("HEre?")
    if form.validate_on_submit():
        print("Here1?")
        mydb.reconnect()  # reconnection to server
        mycursor = mydb.cursor()
        sql = "SELECT * FROM userdata WHERE email = %s"
        mycursor.execute(sql, [form.email.data])
        user = mycursor.fetchone()

        if not user:
            return render_template('password_reset.html', form=form, error="Invalid email!")
        print("Email to send",user[2])
        send_reset_link(user[2])
        return render_template('LoginPage.html', error = "Reset password email sent")

    return render_template('password_reset.html', form=form)

def token_reset(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        return redirect(url_for('login'),error="Password reset link is invalid.")

    form = ResetPasswordForm()

    if form.validate_on_submit():
        mydb.reconnect()  # reconnection to server
        mycursor = mydb.cursor()
        sql = "SELECT * FROM userdata WHERE email = %s"
        mycursor.execute(sql, [email])
        user = mycursor.fetchone()

        if not user :
            return redirect(url_for('login'),error="Invalid email!")

        errorlist = ""
        password = form.password.data
        if len(password) < 8 :
            errorlist += ", password too short"
        if not any(x.isupper() for x in password) :
            errorlist += ", no uppercase characters"
        if not any(x.islower() for x in password) :
            errorlist += ", no lowercase characters"

        if errorlist != "" :
            errorlist = "Error" + errorlist + "."
            return render_template('LoginPage.html', error=errorlist)


        salt = (user[4]).encode() #grab the salt and encode
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000).decode('latin1')

        sql = 'UPDATE userdata SET password = %s WHERE email = %s'
        val = (hashed_password,email)
        mycursor.execute(sql,val)
        mydb.commit()


        return render_template('LoginPage.html', error = "Password Changed")

    return render_template('reset_token_pass.html',token=token, form=form)

