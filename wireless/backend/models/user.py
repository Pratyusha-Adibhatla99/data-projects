from flask_login import UserMixin
from backend.models.db import db # Updated Import

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)