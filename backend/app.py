from routes.job_routes import job_router
from routes.user_routes import user_router
from routes.company_routes import company_router
from routes.application_routes import application_router
from flask import Flask, request, jsonify, redirect
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv
from db import db, close_db
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from flasgger import Swagger

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Register the blueprints
app.register_blueprint(user_router, url_prefix='/api/users')
app.register_blueprint(job_router, url_prefix='/api/jobs')
app.register_blueprint(company_router, url_prefix='/api/companies')
app.register_blueprint(application_router, url_prefix='/api/applications')

# Initialize Swagger with security definitions
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Job Finder API",
        "description": "API for Job Finder application",
        "version": "1.0"
    },
    "securityDefinitions": {
        "bearerAuth": {  # Security scheme name matching your OpenAPI definition
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "security": [  # Apply security globally
        {
            "bearerAuth": []  # Match the name of the security scheme
        }
    ],
    "basePath": "/api",  # Base path for blueprint registration
})

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    File Upload
    ---
    tags:
      - File Upload
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The file to upload
    responses:
      201:
        description: File uploaded successfully
      400:
        description: Bad request
    """
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
