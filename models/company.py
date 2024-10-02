from db import db


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    website_url = db.Column(db.String(255), nullable=False)
    company_size = db.Column(db.String(50), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(255), nullable=True)  # Optional logo URL
    contact_email = db.Column(db.String(100), nullable=False)

    jobs = db.relationship('Job', backref='company', lazy=True)
