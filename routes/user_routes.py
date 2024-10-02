from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

user_router = Blueprint('user', __name__)


@user_router.route('/register', methods=['POST'])
def register_user():
    db: Session = get_db()

    # Extracting data from request
    data = request.json
    if not data or not all(key in data for key in ['fullname', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_user = User.find_by_email(db, data['email'])
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        fullname=data['fullname'],
        email=data['email'],
        role='job_seeker',  # Default role, can be modified as needed
        password_hash=hashed_password
    )
    new_user.save(db)
    return jsonify(new_user.to_dict()), 201


@user_router.route('/login', methods=['POST'])
def login():
    db: Session = get_db()

    # Extracting data from request
    data = request.json
    if not data or any(key not in data for key in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.find_by_email(db, data['email'])
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(message='Login successful', access_token=access_token)


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

    data = request.json
    for key, value in data.items():
        if key == 'password':
            setattr(user, 'password_hash', generate_password_hash(value))
        else:
            setattr(user, key, value)

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
    return '', 204
