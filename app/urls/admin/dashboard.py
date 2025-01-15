from flask import Blueprint, Flask, request, jsonify
from sqlalchemy import desc, text, func
import datetime


# Blueprint Configuration
dashboard_url = Blueprint(
    "dashboard_url", __name__, template_folder="html", static_folder="static"
)

from app import db