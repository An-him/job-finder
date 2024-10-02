from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from db import get_db
from models.job import Job
from datetime import datetime
from services.job_service import search_jobs

job_router = Blueprint('job', __name__)


@job_router.route('/search', methods=['GET'])
def search_job():
    # Get the search query from request parameters
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    jobs = search_jobs(query)  # Call the job search function
    if jobs is None:
        return jsonify({'error': 'Failed to fetch job listings'}), 500

    return jsonify(jobs), 200


@job_router.route('/', methods=['POST'])
@jwt_required()
def create_job():
    db: Session = get_db()  # Get the current database session
    job_data = request.json

    # Validate required fields
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
        job_status='active',  # Default status
        application_link=job_data['application_link']
    )

    new_job.save(db)  # Save the new job to the database
    return jsonify(new_job.to_dict()), 201


@job_router.route('/', methods=['GET'])
def get_jobs():
    db: Session = get_db()  # Get the current database session
    jobs = Job.query.all()  # Fetch all jobs
    return jsonify([job.to_dict() for job in jobs]), 200


@job_router.route('/<int:job_id>', methods=['GET'])
def get_job(job_id: int):
    db: Session = get_db()  # Get the current database session
    job = Job.query.get(job_id)  # Fetch job by ID
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job.to_dict()), 200


@job_router.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id: int):
    db: Session = get_db()  # Get the current database session
    job = Job.query.get(job_id)  # Fetch job by ID
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    job_data = request.json
    for key, value in job_data.items():
        setattr(job, key, value)

    job.save(db)  # Save the updated job to the database
    return jsonify(job.to_dict()), 200


@job_router.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id: int):
    db: Session = get_db()  # Get the current database session
    job = Job.query.get(job_id)  # Fetch job by ID
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    job.delete(db)  # Delete the job from the database
    return '', 204