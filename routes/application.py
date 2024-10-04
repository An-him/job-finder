from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from db import get_db
from models.application import Application
from models.job import Job
from models.user import User
from datetime import datetime

application_router = Blueprint('application', __name__)


@application_router.route('/apply', methods=['POST'])
@jwt_required()
def apply_for_job():
    db: Session = get_db()
    user_id = get_jwt_identity()  # Get the current user's ID
    application_data = request.json

    if not application_data or 'job_id' not in application_data:
        return jsonify({'error': 'Missing required fields'}), 400

    job = Job.query.get(application_data['job_id'])
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    # Check if the user has already applied for this job
    existing_application = Application.query.filter_by(user_id=user_id, job_id=application_data['job_id']).first()
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
def get_application(application_id: int):
    db: Session = get_db()
    application = Application.query.get(application_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    return jsonify(application.to_dict()), 200


@application_router.route('/user_applications', methods=['GET'])
@jwt_required()
def get_user_applications():
    db: Session = get_db()
    user_id = get_jwt_identity()  # Get the current user's ID
    applications = Application.query.filter_by(user_id=user_id).all()
    
    return jsonify([application.to_dict() for application in applications]), 200


@application_router.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
def withdraw_application(application_id: int):
    db: Session = get_db()
    application = Application.query.get(application_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    application.status = 'withdrawn'
    application.save(db)
    
    return jsonify({'message': 'Application withdrawn successfully'}), 200
