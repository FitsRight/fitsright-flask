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
   query = text("""
      SELECT info FROM public.standard_texts
      WHERE st_id='4e8c697f-0342-4aa2-abe2-14468d739d7e'
      ORDER BY st_id ASC 
         """)
   row = db.session.execute(query).fetchone()
   standard_text = row[0] if row else ""

   return render_template('/home/privacy_policy.html', standard_text=standard_text)

@home_url.route("/terms-of-service/", methods=['GET','POST'])
def terms_of_service():
   query = text("""
      SELECT info FROM public.standard_texts
      WHERE st_id='ed41df63-2fdb-4626-9fac-74876183ac1c'
      ORDER BY st_id ASC 
         """)
   row = db.session.execute(query).fetchone()
   standard_text = row[0] if row else ""

   return render_template('/home/terms_of_service.html', standard_text=standard_text)

@home_url.route("/acceptable-use-policy/", methods=['GET','POST'])
def acceptable_use_policy():
   query = text("""
      SELECT info FROM public.standard_texts
      WHERE st_id='0ac2d4df-d122-4dbf-9348-0ac687dcd4f0'
      ORDER BY st_id ASC 
         """)
   row = db.session.execute(query).fetchone()
   standard_text = row[0] if row else ""

   return render_template('/home/acceptable_use_policy.html', standard_text=standard_text)

@home_url.route("/cookie-policy/", methods=['GET','POST'])
def cookie_policy():
   query = text("""
      SELECT info FROM public.standard_texts
      WHERE st_id='542f7163-99d4-4cfd-97ca-c5e06dc84527'
      ORDER BY st_id ASC 
         """)
   row = db.session.execute(query).fetchone()
   standard_text = row[0] if row else ""

   return render_template('/home/cookie_policy.html', standard_text=standard_text)


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

@home_url.route("/admin/retailer_sizes/<int:rref>", methods=['GET'])
@login_required
def admin_retailers_sizes(rref):
   if current_user.is_authenticated:
      return render_template('/admin/retailers_sizes.html', rref=rref)
   else:
      return redirect('/login')
   
@home_url.route("/admin/retailer_links/<int:rref>", methods=['GET'])
@login_required
def admin_retailers_links(rref):
   if current_user.is_authenticated:
      query = text("""
      SELECT 
         r.retailers_id, 
         r.name
      FROM 
         public.retailers r
      ORDER BY 
         r.name ASC;
            """)
      retailers = db.session.execute(query).fetchall()        
      return render_template('/admin/retailer_links.html', rref=rref, retailers=retailers)
   else:
      return redirect('/login')

   
@home_url.route("/admin/sizes", methods=['GET','POST'])
@login_required
def admin_sizes():
   if current_user.is_authenticated:
      return render_template('/admin/sizes.html')
   else:
      return redirect('/login')

@home_url.route("/admin/promotions", methods=['GET','POST'])
@login_required
def admin_promotions():
   if current_user.is_authenticated:
      query = text("""
      SELECT 
         r.retailers_id, 
         r.name
      FROM 
         public.retailers r
      ORDER BY 
         r.name ASC;
            """)
      retailers = db.session.execute(query).fetchall() 
      return render_template('/admin/promotions.html', retailers=retailers)
   else:
      return redirect('/login')

@home_url.route("/admin/locations", methods=['GET','POST'])
@login_required
def admin_locations():
   if current_user.is_authenticated:
      query = text("""
      SELECT * FROM public.scanner_locations ORDER BY id ASC 
            """)
      retailers = db.session.execute(query).fetchall() 
      return render_template('/admin/locations.html', retailers=retailers)
   else:
      return redirect('/login')

@home_url.route("/admin/users", methods=['GET','POST'])
@login_required
def users_retailers():
   if current_user.is_authenticated:
      return render_template('/admin/users.html')
   else:
      return redirect('/login')

@home_url.route("/admin/categories", methods=['GET','POST'])
@login_required
def admin_categories():
   return render_template('/admin/categories.html')

@home_url.route("/admin/dashboard", methods=['GET','POST'])
@login_required
def dashboard_retailers():
   return render_template('/admin/dashboard.html')

@home_url.route("/admin/logout", methods=['GET','POST'])
def admin_logout():
   logout_user()
   return redirect('/login')

@home_url.route("/admin/settings", methods=['GET','POST'])
@login_required
def users_settings():
   if current_user.is_authenticated:
      return render_template('/admin/settings.html')
   else:
      return redirect('/login')


@home_url.route("/admin/measurements", methods=['GET','POST'])
@login_required
def measurements():
   if current_user.is_authenticated:
      return render_template('/admin/measurements.html')
   else:
      return redirect('/login')
   
@home_url.route("/admin/standard_text", methods=['GET','POST'])
@login_required
def standard_text():
   if current_user.is_authenticated:
      return render_template('/admin/standard_text.html')
   else:
      return redirect('/login')
