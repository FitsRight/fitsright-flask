import hashlib
from flask_login import UserMixin
from sqlalchemy import TIMESTAMP, Boolean, Column, Date, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash
from sqlalchemy.ext.declarative import DeclarativeMeta

from app import db

BaseModel: DeclarativeMeta = db.Model

class User(UserMixin, BaseModel):  # Inherit directly from db.Model
    __tablename__ = 'users_customers'
    __table_args__ = {"schema": "public"}

    users_customers_id = Column(Integer, primary_key=True, autoincrement=True)
    onesignal_id = Column(Text)
    tg3d_id = Column(Text)
    full_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False, unique=True)  # Add unique constraint
    google_access_token = Column(String(255))
    google_user_id = Column(String(255))
    login_from = Column(String(255))
    facebook_access_token = Column(String(255))
    facebook_user_id = Column(String(255))
    user_password = Column(String(255), nullable=False)
    user_phone = Column(String(255))
    profile_image = Column(String(255))
    packages_id = Column(Integer)
    system_genders_id = Column(Integer)
    date_of_birth = Column(Date)
    uk_cities_id = Column(Integer)
    terms_agreements = Column(Text, nullable=False)
    notification_switch = Column(Text)
    sizes_units_id = Column(Integer)
    sizes_uk_id = Column(Integer)
    neck = Column(Numeric(15, 2))
    sleeves_length = Column(Numeric(15, 2))
    chest = Column(Numeric(15, 2))
    under_bust = Column(Numeric(15, 2))
    waist = Column(Numeric(15, 2))
    hip = Column(Numeric(15, 2))
    shoulder = Column(Numeric(15, 2))
    height = Column(Numeric(15, 2))
    belly = Column(Numeric(15, 2))
    calf = Column(Numeric(15, 2))
    thigh = Column(Numeric(15, 2))
    inside_leg_length = Column(Numeric(15, 2))
    verify_otp = Column(Integer, default=0)
    is_verified = Column(Text, default='No')
    reset_otp = Column(Integer, default=0)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP, nullable=False)
    status = Column(Text, nullable=False)
    profile_img = Column(Text)
    user_tokens = Column(Integer)
    is_admin = Column(Boolean, default=False)

    def __init__(self, full_name, user_email, user_password):
        self.full_name = full_name
        self.user_email = user_email
        self.set_password(user_password)

    def get_id(self):
        return self.users_customers_id  # Flask-Login will use this

    def set_password(self, password):
        self.user_password = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return self.user_password == hashlib.md5(password.encode()).hexdigest()

    def to_dict(self):
        return {
            "user_customers_id": self.users_customers_id,
            "full_name": self.full_name,
            "user_email": self.user_email,  # Fixed this
            "is_verified": self.is_verified,
            "status": self.status
        }

    def __repr__(self):
        return f"<User {self.user_email}>"
