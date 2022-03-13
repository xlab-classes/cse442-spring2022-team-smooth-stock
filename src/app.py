from flask import Flask, render_template
import os

t_dir = os.path.abspath('../html')
app = Flask(__name__, template_folder=t_dir)


@app.route('/')
def hello_world():
   return render_template('CreateAccount.html')

@app.route('/news')
def return_news():
   return render_template('news.html')

@app.route('/createaccount')
def return_create_acc():
   return render_template('CreateAccount.html')

@app.route('/landingpage')
def return_landing_page():
   return render_template('LandingPage.html')

@app.route('/notify')
def return_notify_page():
   return render_template('notify.html')

@app.route('/discover')
def return_discover_page():
   return render_template('discover.html')

if __name__ == '__main__':
   app.run()