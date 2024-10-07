from flask_sqlalchemy import SQLAlchemy
from flask import g
# from db.db import get_db

# Create a new instance of SQLAlchemy
db = SQLAlchemy()


def get_db():
    """Get the current database session."""
    if 'db' not in g:
        g.db = db.session
    return g.db


def close_db(e=None):
    """Remove the database session at the end of the request."""
    db.session.remove()
