from models.application import Application
from models.job import Job
from models.company import Company
from models.user import User
from routes.user_routes import user_router
from routes.job_routes import job_router
from routes.company_routes import company_router
from routes.application_routes import application_router
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv
from db import db, close_db
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# File upload configuration
# Set the upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400


# Register the blueprints
app.register_blueprint(user_router, url_prefix='/api/users')
app.register_blueprint(job_router, url_prefix='/api/jobs')
app.register_blueprint(company_router, url_prefix='/api/companies')
app.register_blueprint(application_router, url_prefix='/api/applications')


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
def home():
    return render_template('index.html')


@app.route('/register.html')
def register():
    return render_template('register.html')


@app.route('/job_seeker_dashboard.html')
def dashboard():
    return render_template('job_seeker_dashboard.html')


@app.route('/login.html')
def login():
    return render_template('login.html')


@app.route('/jobs.html')
def jobs_page():
    return render_template('jobs.html')


if __name__ == '__main__':
    app.run(debug=True)
