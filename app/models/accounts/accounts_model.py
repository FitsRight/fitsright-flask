"""Database models."""
import os
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from sqlalchemy.ext.declarative import DeclarativeMeta

BaseModel: DeclarativeMeta = db.Model


class User(UserMixin, BaseModel):
    """User account model."""

    __table_args__ = {"schema": "public"}
    __tablename__ = "accounts"
    id = db.Column(UUID(), primary_key=True, unique=True, default=uuid4())
   

    def __init__(self, id):
        self.id = id


    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        """Check hashed password."""
    
        return check_password_hash(self.password, password),
    
    def to_dict(self):
        """Convert User object to dictionary for JSON serialization."""
        return {
            "id": str(self.id),  # Convert UUID to string for JSON compatibility
        }

    def __repr__(self):
        return "<User {}>".format(self.email)