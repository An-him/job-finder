from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from db import get_db
from models.application import Application
from models.job import Job
from models.user import User
from datetime import datetime
from flasgger import swag_from

application_router = Blueprint('application', __name__)


@application_router.route('/apply', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': 'Apply for a job',
    'description': 'Allows a user to apply for a job by submitting an application.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'job_id': {'type': 'integer'},
                    'cover_letter': {'type': 'string'}
                },
                'required': ['job_id']
            },
            'description': 'The job application details, including the job_id and an optional cover letter.'
        }
    ],
    'responses': {
        '201': {
            'description': 'Job application created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'job_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'cover_letter': {'type': 'string'},
                    'application_date': {'type': 'string'},
                    'status': {'type': 'string'}
                }
            }
        },
        '400': {'description': 'Missing required fields or application already exists'},
        '404': {'description': 'Job not found'}
    }
})
def apply_for_job():
    db: Session = get_db()
    user_id = get_jwt_identity()  # Get the current user's ID
    application_data = request.json

    if not application_data or 'job_id' not in application_data:
        return jsonify({'error': 'Missing required fields'}), 400

    job = Job.query.get(application_data['job_id'])
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    existing_application = Application.query.filter_by(
        user_id=user_id, job_id=application_data['job_id']).first()
    if existing_application:
        return jsonify({'error': 'You have already applied for this job'}), 400

    new_application = Application(
        job_id=application_data['job_id'],
        user_id=user_id,
        cover_letter=application_data.get('cover_letter', ''),
        application_date=datetime.utcnow(),
        status='submitted'
    )

    new_application.save(db)
    return jsonify(new_application.to_dict()), 201


@application_router.route('/<int:application_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': 'Get a specific application by ID',
    'description': 'Retrieve details of a specific application by its ID.',
    'parameters': [
        {
            'name': 'application_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the application to retrieve.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Application details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'job_id': {'type': 'integer'},
                    'user_id': {'type': 'integer'},
                    'cover_letter': {'type': 'string'},
                    'application_date': {'type': 'string'},
                    'status': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'Application not found'}
    }
})
def get_application(application_id: int):
    db: Session = get_db()
    application = Application.query.get(application_id)

    if not application:
        return jsonify({'error': 'Application not found'}), 404

    return jsonify(application.to_dict()), 200


@application_router.route('/user_applications', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': 'Get all applications for the current user',
    'description': 'Retrieve a list of all job applications made by the current user.',
    'responses': {
        '200': {
            'description': 'List of applications',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'job_id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'cover_letter': {'type': 'string'},
                        'application_date': {'type': 'string'},
                        'status': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_user_applications():
    db: Session = get_db()
    user_id = get_jwt_identity()  # Get the current user's ID
    applications = Application.query.filter_by(user_id=user_id).all()

    return jsonify([application.to_dict() for application in applications]), 200


@application_router.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': 'Withdraw an application',
    'description': 'Allows a user to withdraw a specific job application by changing its status to "withdrawn".',
    'parameters': [
        {
            'name': 'application_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the application to withdraw.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Application withdrawn successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'Application not found'}
    }
})
def withdraw_application(application_id: int):
    db: Session = get_db()
    application = Application.query.get(application_id)

    if not application:
        return jsonify({'error': 'Application not found'}), 404

    application.status = 'withdrawn'
    application.save(db)

    return jsonify({'message': 'Application withdrawn successfully'}), 200
