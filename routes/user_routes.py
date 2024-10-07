from flask import Blueprint, request, jsonify, render_template, url_for
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

user_router = Blueprint('user', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_router.route('/register', methods=['POST'])
def register_user():
    db: Session = get_db()

    # Extracting data from request
    data = request.form  # Use request.form for form-data
    if not data or not all(key in data for key in ['fullname', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_user = User.find_by_email(db, data['email'])
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        fullname=data['fullname'],
        email=data['email'],
        role='job_seeker',  # Default role
        password_hash=hashed_password
    )

    # Handle file uploads for profile picture and resume
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(UPLOAD_FOLDER, filename))
            new_user.profile_picture = filename

    if 'resume' in request.files:
        resume = request.files['resume']
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume.save(os.path.join(UPLOAD_FOLDER, filename))
            new_user.resume = filename

    new_user.save(db)
    return jsonify(new_user.to_dict()), 201


@user_router.route('/login', methods=['POST'])
def login():
    db: Session = get_db()
    data = request.json
    if not data or any(key not in data for key in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.find_by_email(db, data['email'])
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)

    # Redirect based on user role
    if user.role == 'job_seeker':
        # Use the endpoint name
        redirect_url = url_for('user.job_seeker_dashboard')
    elif user.role == 'recruiter':
        # Use the endpoint name
        redirect_url = url_for('user.recruiter_dashboard')
    else:
        return jsonify({'error': 'Invalid role'}), 403

    return jsonify({'message': 'Login successful',
                    'access_token': access_token,
                    'redirect_url': redirect_url,
                    'user': user.to_dict()
                    }), 200


@user_router.route('/job_seeker_dashboard')
@jwt_required()
def job_seeker_dashboard():
    current_user_id = get_jwt_identity()
    db: Session = get_db()
    user = User.find_by_id(db, current_user_id)
    if not user or user.role != 'job_seeker':
        return jsonify({'error': 'Unauthorized'}), 403
    return render_template('job_seeker_dashboard.html')


@user_router.route('/recruiter_dashboard')
@jwt_required()
def recruiter_dashboard():
    current_user_id = get_jwt_identity()
    db: Session = get_db()
    user = User.find_by_id(db, current_user_id)
    if not user or user.role != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403
    return render_template('recruiter_dashboard.html')

@user_router.route('/', methods=['GET'])
@jwt_required()
def get_users():
    db: Session = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    query = User.filter_by_fullname(db, search)
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'items': [user.to_dict() for user in users],
        'total': total,
        'page': page,
        'per_page': per_page
    })


@user_router.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id: int):
    db: Session = get_db()
    if user := User.find_by_id(db, user_id):
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@user_router.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id: int):
    db: Session = get_db()
    current_user_id = get_jwt_identity()

    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.find_by_id(db, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.form  # Use request.form for updates
    for key, value in data.items():
        if key == 'password':
            setattr(user, 'password_hash', generate_password_hash(value))
        else:
            setattr(user, key, value)

    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(UPLOAD_FOLDER, filename))
            user.profile_picture = filename

    if 'resume' in request.files:
        resume = request.files['resume']
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume.save(os.path.join(UPLOAD_FOLDER, filename))
            user.resume = filename

    user.save(db)
    return jsonify(user.to_dict()), 200


@user_router.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id: int):
    db: Session = get_db()
    current_user_id = get_jwt_identity()

    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.find_by_id(db, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.delete(db)
    return jsonify(message='User deleted successfully'), 204
