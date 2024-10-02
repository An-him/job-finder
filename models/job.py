from db import db
from datetime import datetime


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), default="Remote")
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    application_deadline = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'companies.id'), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    job_status = db.Column(db.String(20), default='active')
    application_link = db.Column(db.String(255), nullable=False)

    company = db.relationship('Company', backref=db.backref('jobs', lazy=True))
