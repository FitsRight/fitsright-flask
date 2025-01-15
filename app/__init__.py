"""Initialize app."""
from flask import Flask, make_response
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()

def create_app():
    """Construct the core app object."""
    app = Flask(__name__, instance_relative_config=False, template_folder="html")
    app.config.from_object("config.Config")

    # Initialize Plugins
    db.init_app(app)
    mail = Mail(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    with app.app_context():
        # Register Blueprints
       
        from app.urls.home.home_url import home_url
        from app.urls.admin.retailers import retailers_url
        from app.urls.calls.login_url import login_url
        from app.urls.admin.users import users_url
        from app.urls.admin.dashboard import dashboard_url
 
        app.register_blueprint(home_url)
        app.register_blueprint(login_url)
        app.register_blueprint(retailers_url)
        app.register_blueprint(users_url)
        app.register_blueprint(dashboard_url)

        # Create Database Models
        db.create_all()
        db.session.commit()

        # Compile static assets
        # if app.config["FLASK_ENV"] == "development":
        #     compile_static_assets(app)
        return app
