import hashlib
from flask import Blueprint, Flask, flash, redirect, request, jsonify, url_for
from flask_login import UserMixin, login_user
from sqlalchemy import desc, text, func
from app.models.accounts.accounts_model import User
from app import db, login_manager

# Blueprint Configuration
login_url = Blueprint(
    "login_url", __name__, template_folder="html", static_folder="static"
)

from app import db

        
# Flask route to handle the user login
@login_url.route('/login_check', methods=['POST'])
def login():
    try:
        data = request.get_json()
        # Validate required fields
        user_email = data.get('user_email').strip()
        user_password = data.get('user_password').strip()
        hashed_password = hashlib.md5(user_password.encode()).hexdigest()
        user = User.query.filter_by(user_email=user_email).first()
        if user:
            if user and user.user_password == hashed_password.strip():
                login_user(user)
                return jsonify({}),200
        # else:
        #     print(f"{user.user_password} does not match {hashed_password}")
        return jsonify({}),401
    except Exception as e:
        # print(e)
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
    

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if user_id is not None:
        # print(user_id)
        return User.query.filter_by(users_customers_id=user_id).first()
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash("You must be logged in to view that page.")
    return redirect(url_for("home_url.login"))