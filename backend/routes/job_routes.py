from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from db import get_db
from models.job import Job
from datetime import datetime
from services.job_service import search_jobs
from flasgger import swag_from

job_router = Blueprint('job', __name__)


@job_router.route('/search', methods=['GET'])
@swag_from({
    'tags': ['Jobs'],
    'summary': 'Search jobs by query',
    'description': 'Allows users to search for jobs using a query string parameter.',
    'parameters': [
        {
            'name': 'q',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The search query for job listings.'
        }
    ],
    'responses': {
        '200': {
            'description': 'A list of job results',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'job_title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'company': {'type': 'string'},
                        'location': {'type': 'string'}
                    }
                }
            }
        },
        '400': {'description': 'Missing query parameter'},
        '500': {'description': 'Failed to fetch job listings'}
    }
})
def search_job():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    jobs = search_jobs(query)
    if jobs is None:
        return jsonify({'error': 'Failed to fetch job listings'}), 500

    return jsonify(jobs), 200


@job_router.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Jobs'],
    'summary': 'Create a new job',
    'description': 'Allows authenticated users to create a new job listing by providing required fields.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'job_title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'job_type': {'type': 'string'},
                    'category': {'type': 'string'},
                    'company_id': {'type': 'integer'},
                    'experience_level': {'type': 'string'},
                    'application_link': {'type': 'string'},
                    'location': {'type': 'string'},
                    'application_deadline': {'type': 'string', 'format': 'date'}
                },
                'required': ['job_title', 'description', 'job_type', 'category', 'company_id', 'experience_level', 'application_link']
            },
            'description': 'The details of the job to be created.'
        }
    ],
    'responses': {
        '201': {
            'description': 'Job created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'job_title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'job_type': {'type': 'string'},
                    'location': {'type': 'string'},
                    'application_deadline': {'type': 'string', 'format': 'date'},
                    'category': {'type': 'string'},
                    'company_id': {'type': 'integer'},
                    'experience_level': {'type': 'string'},
                    'application_link': {'type': 'string'}
                }
            }
        },
        '400': {'description': 'Missing required fields'}
    }
})
def create_job():
    db: Session = get_db()
    job_data = request.json

    if not job_data or not all(key in job_data for key in ['job_title', 'description', 'job_type', 'category', 'company_id', 'experience_level', 'application_link']):
        return jsonify({'error': 'Missing required fields'}), 400

    new_job = Job(
        job_title=job_data['job_title'],
        description=job_data['description'],
        job_type=job_data['job_type'],
        location=job_data.get('location', 'Remote'),
        date_posted=datetime.utcnow(),
        application_deadline=job_data.get('application_deadline'),  # Optional
        category=job_data['category'],
        company_id=job_data['company_id'],
        experience_level=job_data['experience_level'],
        job_status='active',
        application_link=job_data['application_link']
    )

    new_job.save(db)
    return jsonify(new_job.to_dict()), 201


@job_router.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Jobs'],
    'summary': 'Get all jobs',
    'description': 'Retrieve a list of all job postings for authenticated users.',
    'responses': {
        '200': {
            'description': 'A list of jobs',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'job_title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'job_type': {'type': 'string'},
                        'location': {'type': 'string'},
                        'application_deadline': {'type': 'string', 'format': 'date'},
                        'category': {'type': 'string'},
                        'company_id': {'type': 'integer'},
                        'experience_level': {'type': 'string'},
                        'job_status': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_jobs():
    db: Session = get_db()
    jobs = Job.query.all()
    return jsonify([job.to_dict() for job in jobs]), 200


@job_router.route('/<int:job_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Jobs'],
    'summary': 'Get a specific job by ID',
    'description': 'Retrieve the details of a job posting by its ID for authenticated users.',
    'parameters': [
        {
            'name': 'job_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the job to retrieve.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Job details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'job_title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'job_type': {'type': 'string'},
                    'location': {'type': 'string'},
                    'application_deadline': {'type': 'string', 'format': 'date'},
                    'category': {'type': 'string'},
                    'company_id': {'type': 'integer'},
                    'experience_level': {'type': 'string'},
                    'job_status': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'Job not found'}
    }
})
def get_job(job_id: int):
    db: Session = get_db()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job.to_dict()), 200


@job_router.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Jobs'],
    'summary': 'Update a job by ID',
    'description': 'Allows authenticated users to update an existing job posting by its ID.',
    'parameters': [
        {
            'name': 'job_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the job to update.'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'job_title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'job_type': {'type': 'string'},
                    'location': {'type': 'string'},
                    'application_deadline': {'type': 'string', 'format': 'date'},
                    'category': {'type': 'string'},
                    'experience_level': {'type': 'string'},
                    'job_status': {'type': 'string'},
                    'application_link': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Job updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'job_title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'job_type': {'type': 'string'},
                    'location': {'type': 'string'},
                    'application_deadline': {'type': 'string', 'format': 'date'},
                    'category': {'type': 'string'},
                    'experience_level': {'type': 'string'},
                    'job_status': {'type': 'string'},
                    'application_link': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'Job not found'}
    }
})
def update_job(job_id: int):
    db: Session = get_db()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    job_data = request.json
    for key, value in job_data.items():
        setattr(job, key, value)

    job.save(db)
    return jsonify(job.to_dict()), 200


@job_router.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Jobs'],
    'summary': 'Delete a job by ID',
    'description': 'Allows authenticated users to delete a job posting by its ID.',
    'parameters': [
        {
            'name': 'job_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the job to delete.'
        }
    ],
    'responses': {
        '204': {'description': 'Job deleted successfully'},
        '404': {'description': 'Job not found'}
    }
})
def delete_job(job_id: int):
    db: Session = get_db()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    job.delete(db)
    return jsonify({'message': 'Job deleted successfully'}), 204
