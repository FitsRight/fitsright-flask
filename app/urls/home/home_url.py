import datetime
from uuid import uuid4
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from sqlalchemy import desc, text, func
import pathlib

from app.models.accounts.accounts_model import User
from app import db, login_manager


# Blueprint Configuration
home_url = Blueprint(
    "home_url", __name__, template_folder="html", static_folder="static"
)

PARENT_PATH = str(pathlib.Path(__file__).parent.resolve())

UPLOAD_FOLDER = "app/static/uploads/"


@home_url.route("/", methods=['GET','POST'])
def home():
   return render_template('home/home.html')

@home_url.route("/privacy-policy/", methods=['GET','POST'])
def privacy_policy():
   return render_template('home/privacy_policy.html')

@home_url.route("/terms-of-service/", methods=['GET','POST'])
def terms_of_service():
   return render_template('home/terms_of_service.html')

@home_url.route("/acceptable-use-policy/", methods=['GET','POST'])
def acceptable_use_policy():
   return render_template('home/acceptable_use_policy.html')

@home_url.route("/cookie-policy/", methods=['GET','POST'])
def cookie_policy():
   return render_template('home/cookie_policy.html')

@home_url.route("/login/", methods=['GET','POST'])
def login():
   return render_template('home/login.html')

@home_url.route("/admin/retailers", methods=['GET','POST'])
@login_required
def admin_retailers():
   if current_user.is_authenticated:
      return render_template('/admin/retailers.html')
   else:
      return redirect('/login')

@home_url.route("/admin/users", methods=['GET','POST'])
@login_required
def users_retailers():
   if current_user.is_authenticated:
      return render_template('/admin/users.html')
   else:
      return redirect('/login')


@home_url.route("/admin/dashboard", methods=['GET','POST'])
@login_required
def dashboard_retailers():
   return render_template('/admin/dashboard.html')

@home_url.route("/admin/logout", methods=['GET','POST'])
def admin_logout():
   logout_user()
   return redirect('/login')
