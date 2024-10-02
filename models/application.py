from db import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    # applied, under_review, accepted, rejected
    status = db.Column(db.String(50), default='applied')
    # Optional if different from user's resume
    resume = db.Column(db.String(255), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)  # Optional

    job = db.relationship('Job', backref=db.backref('applications', lazy=True))
