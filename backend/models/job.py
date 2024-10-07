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

    company = db.relationship('Company', back_populates='jobs', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'description': self.description,
            'job_type': self.job_type,
            'location': self.location,
            'date_posted': self.date_posted,
            'application_deadline': self.application_deadline,
            'category': self.category,
            'company_id': self.company_id,
            'experience_level': self.experience_level,
            'job_status': self.job_status,
            'application_link': self.application_link
        }

    def save(self, db_session):
        """Add and commit the current instance to the database."""
        db_session.add(self)
        db_session.commit()

    def delete(self, db_session):
        """Delete the current instance from the database."""
        db_session.delete(self)
        db_session.commit()

    def update(self, db_session, **kwargs):
        """Update the current instance with the given kwargs."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        db_session.commit()

    @classmethod
    def find_by_id(cls, db_session, job_id):
        """Find a job by its ID."""
        return db_session.query(cls).filter_by(id=job_id).first()
