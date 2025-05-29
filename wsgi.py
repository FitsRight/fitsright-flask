"""Application entry point."""
import os
import shutil
from flask_login import current_user
from app import create_app
from flask import make_response, render_template, request, redirect, session
from flask_mail import Mail
from flask_session.__init__ import Session
from flask_mobility import Mobility
import datetime
import sys

app = create_app()
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DEBUG'] = True

# Configuration

app.config['SECRET_KEY'] = '2d427f45-9aea-4e7b-b361-cd9ba5eea63a'
app.config['MAIL_SERVER'] = 'smtp.office365.com'
# app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'customerservice@fitsright.co.uk'
app.config['MAIL_DEFAULT_SENDER'] = 'customerservice@fitsright.co.uk'
app.config['MAIL_PASSWORD'] = ')A@i*#%off$3'

Session(app)
Mobility(app)
mail = Mail(app)


if __name__ == "__main__":
    sys.setrecursionlimit(2097152)    # adjust numbers
    # app.run()
    app.run(debug=True)
