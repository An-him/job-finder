from datetime import datetime
from db import db

from sqlalchemy.orm import Session


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
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

    def __init__(self, fullname, email, password_hash, role):
        self.fullname = fullname
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'role': self.role,
            'date_created': self.date_created.isoformat()
        }

    @classmethod
    def find_by_email(cls, db, email):
        """
        Find a user by email.
        """
        return db.query(cls).filter_by(email=email).first()

    @classmethod
    def filter_by_fullname(cls, db_session, fullname):
        return db_session.query(cls).filter(cls.fullname.ilike(f"%{fullname}%"))

    @classmethod
    def find_by_id(cls, db: Session, user_id: int):
        """
        Find a user by ID.
        """
        return db.query(cls).filter_by(id=user_id).first()

    def save(self, db: Session):
        """
        Save the user to the database.
        """
        db.add(self)
        db.commit()

    def delete(self, db: Session):
        """Delete the user from the database."""
        db.delete(self)
        db.commit()
