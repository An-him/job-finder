from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from db import get_db
from models.company import Company

company_router = Blueprint('company', __name__)


@company_router.route('/', methods=['POST'])
@jwt_required()
def create_company():
    db: Session = get_db()
    company_data = request.json

    if not all(key in company_data for key in ['company_name', 'description', 'website_url', 'company_size', 'industry', 'contact_email']):
        return jsonify({'error': 'Missing required fields'}), 400

    new_company = Company(
        company_name=company_data['company_name'],
        description=company_data['description'],
        website_url=company_data['website_url'],
        company_size=company_data['company_size'],
        industry=company_data['industry'],
        contact_email=company_data['contact_email']
    )

    new_company.save(db)
    return jsonify(new_company.to_dict()), 201


@company_router.route('/', methods=['GET'])
def get_companies():
    db: Session = get_db()
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies]), 200


@company_router.route('/<int:company_id>', methods=['GET'])
def get_company(company_id: int):
    db: Session = get_db()
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify(company.to_dict()), 200


@company_router.route('/<int:company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id: int):
    db: Session = get_db()
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    company_data = request.json
    for key, value in company_data.items():
        setattr(company, key, value)

    company.save(db)
    return jsonify(company.to_dict()), 200


@company_router.route('/<int:company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id: int):
    db: Session = get_db()
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    company.delete(db)
    return 'message: Company deleted successfully', 204
