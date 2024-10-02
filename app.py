from models.application import Application
from models.job import Job
from models.company import Company
from models.user import User
from routes.user_routes import user_router
from routes.job_routes import job_router
# from routes.company_routes import company_router
# from routes.application_routes import application_router
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv

from db import db, close_db


# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Register the blueprints
app.register_blueprint(user_router, url_prefix='/api/users')
app.register_blueprint(job_router, url_prefix='/api/jobs')
# app.register_blueprint(company_router, url_prefix='/api/companies')
# app.register_blueprint(application_router, url_prefix='/api/applications')


# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize JWT
jwt = JWTManager(app)


# Register teardown function to clean up the database session
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_db()


# Create the database tables if they don't exist
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
