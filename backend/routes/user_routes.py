from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flasgger import swag_from

user_router = Blueprint('user', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_router.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Register a new user',
    'description': 'Allows users to register by providing their details.',
    'parameters': [
        {
            'name': 'fullname',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Full name of the user.'
        },
        {
            'name': 'email',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Email address of the user.'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Password for the user account.'
        },
        {
            'name': 'profile_picture',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Optional profile picture of the user.'
        },
        {
            'name': 'resume',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Optional resume file of the user.'
        }
    ],
    'responses': {
        '201': {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'fullname': {'type': 'string'},
                    'email': {'type': 'string'},
                    'role': {'type': 'string'},
                    'profile_picture': {'type': 'string'},
                    'resume': {'type': 'string'}
                }
            }
        },
        '400': {'description': 'Missing required fields or email already registered'}
    }
})
def register_user():
    db: Session = get_db()

    data = request.form
    if not data or not all(key in data for key in ['fullname', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_user = User.find_by_email(db, data['email'])
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        fullname=data['fullname'],
        email=data['email'],
        role='job_seeker',
        password_hash=hashed_password
    )

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
@swag_from({
    'tags': ['Users'],
    'summary': 'User login',
    'description': 'Allows users to login with their credentials.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'description': 'Email address of the user.'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Password of the user.'
                    }
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'access_token': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'fullname': {'type': 'string'},
                            'email': {'type': 'string'},
                            'role': {'type': 'string'},
                            'profile_picture': {'type': 'string'},
                            'resume': {'type': 'string'}
                        }
                    }
                }
            }
        },
        '400': {
            'description': 'Missing required fields',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        '401': {
            'description': 'Invalid email or password',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def login():
    db: Session = get_db()
    data = request.json
    if not data or any(key not in data for key in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.find_by_email(db, data['email'])
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@user_router.route('/dashboard', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get user dashboard',
    'description': 'Fetches the dashboard for the user.',
    'responses': {
        '200': {'description': 'Dashboard data retrieved successfully'},
        '403': {'description': 'Unauthorized access'}
    }
})
def user_dashboard():
    current_user_id = get_jwt_identity()
    db: Session = get_db()
    user = User.find_by_id(db, current_user_id)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    # Here you would fetch and return relevant dashboard data
    dashboard_data = {
        'user': user.to_dict(),
        # Add other relevant dashboard data here
    }
    return jsonify(dashboard_data), 200

# The rest of your routes (get_users, get_user, update_user, delete_user) can remain largely unchanged,
# just ensure they return JSON responses instead of rendering templates.


@user_router.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get all users',
    'description': 'Fetches a paginated list of all users.',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'description': 'Page number for pagination.',
            'required': False,
            'default': 1
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'description': 'Number of users per page.',
            'required': False,
            'default': 10
        },
        {
            'name': 'search',
            'in': 'query',
            'type': 'string',
            'description': 'Search term for user fullname.',
            'required': False
        }
    ],
    'responses': {
        '200': {
            'description': 'A list of users',
            'schema': {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'fullname': {'type': 'string'},
                                'email': {'type': 'string'},
                                'role': {'type': 'string'},
                                'profile_picture': {'type': 'string'},
                                'resume': {'type': 'string'}
                            }
                        }
                    },
                    'total': {'type': 'integer'},
                    'page': {'type': 'integer'},
                    'per_page': {'type': 'integer'}
                }
            }
        },
        '403': {'description': 'Unauthorized access'}
    },
})
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
@swag_from({
    'tags': ['Users'],
    'summary': 'Get a user by ID',
    'description': 'Fetches user details by user ID.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the user.'
        }
    ],
    'responses': {
        '200': {
            'description': 'User found',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'fullname': {'type': 'string'},
                    'email': {'type': 'string'},
                    'role': {'type': 'string'},
                    'profile_picture': {'type': 'string'},
                    'resume': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'User not found'},
        '403': {'description': 'Unauthorized access'}
    }
})
def get_user(user_id: int):
    db: Session = get_db()
    if user := User.find_by_id(db, user_id):
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@user_router.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Update user details',
    'description': 'Allows a user to update their details.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the user to update.'
        },
        {
            'name': 'fullname',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Full name of the user.'
        },
        {
            'name': 'email',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Email address of the user.'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Password for the user account.'
        },
        {
            'name': 'profile_picture',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Profile picture of the user.'
        },
        {
            'name': 'resume',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Resume file of the user.'
        }
    ],
    'responses': {
        '200': {
            'description': 'User updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'fullname': {'type': 'string'},
                    'email': {'type': 'string'},
                    'role': {'type': 'string'},
                    'profile_picture': {'type': 'string'},
                    'resume': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'User not found'},
        '403': {'description': 'Unauthorized access'}
    }
})
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
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete a user',
    'description': 'Allows a user to delete their account.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the user to delete.'
        }
    ],
    'responses': {
        '204': {'description': 'User deleted successfully'},
        '404': {'description': 'User not found'},
        '403': {'description': 'Unauthorized access'}
    }
})
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
