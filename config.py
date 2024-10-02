import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
