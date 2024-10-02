from datetime import datetime
from db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # recruiter or job seeker
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.Column(db.Text, nullable=True)
    # Optional for job seekers
    location = db.Column(db.String(100), nullable=True)
    # e.g., Junior, Mid, Senior
    experience_level = db.Column(db.String(50), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)  # Optional
    resume = db.Column(db.String(255), nullable=True)  # Optional

    applications = db.relationship('Application', backref='user', lazy=True)
