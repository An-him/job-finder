from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from db import get_db
from models.company import Company
from flasgger import swag_from

company_router = Blueprint('company', __name__)


@company_router.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Companies'],
    'summary': 'Create a new company',
    'description': 'Allows an authenticated user to create a new company by providing required details.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'company_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'website_url': {'type': 'string'},
                    'company_size': {'type': 'string'},
                    'industry': {'type': 'string'},
                    'contact_email': {'type': 'string'}
                },
                'required': ['company_name', 'description', 'website_url', 'company_size', 'industry', 'contact_email']
            },
            'description': 'Company details required for creating a new company.'
        }
    ],
    'responses': {
        '201': {
            'description': 'Company created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'company_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'website_url': {'type': 'string'},
                    'company_size': {'type': 'string'},
                    'industry': {'type': 'string'},
                    'contact_email': {'type': 'string'}
                }
            }
        },
        '400': {'description': 'Missing required fields'}
    }
})
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
@swag_from({
    'tags': ['Companies'],
    'summary': 'Get all companies',
    'description': 'Retrieve a list of all registered companies.',
    'responses': {
        '200': {
            'description': 'A list of companies',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'company_name': {'type': 'string'},
                        'description': {'type': 'string'},
                        'website_url': {'type': 'string'},
                        'company_size': {'type': 'string'},
                        'industry': {'type': 'string'},
                        'contact_email': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_companies():
    db: Session = get_db()
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies]), 200


@company_router.route('/<int:company_id>', methods=['GET'])
@swag_from({
    'tags': ['Companies'],
    'summary': 'Get a specific company by ID',
    'description': 'Retrieve details of a company by its ID.',
    'parameters': [
        {
            'name': 'company_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the company to retrieve.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Company details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'company_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'website_url': {'type': 'string'},
                    'company_size': {'type': 'string'},
                    'industry': {'type': 'string'},
                    'contact_email': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'Company not found'}
    }
})
def get_company(company_id: int):
    db: Session = get_db()
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify(company.to_dict()), 200


@company_router.route('/<int:company_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Companies'],
    'summary': 'Update a company by ID',
    'description': 'Allows an authenticated user to update the details of a company by its ID.',
    'parameters': [
        {
            'name': 'company_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the company to update.'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'company_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'website_url': {'type': 'string'},
                    'company_size': {'type': 'string'},
                    'industry': {'type': 'string'},
                    'contact_email': {'type': 'string'}
                }
            },
            'description': 'Company details to be updated.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Company updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'company_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'website_url': {'type': 'string'},
                    'company_size': {'type': 'string'},
                    'industry': {'type': 'string'},
                    'contact_email': {'type': 'string'}
                }
            }
        },
        '404': {'description': 'Company not found'}
    }
})
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
@swag_from({
    'tags': ['Companies'],
    'summary': 'Delete a company by ID',
    'description': 'Allows an authenticated user to delete a company by its ID.',
    'parameters': [
        {
            'name': 'company_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the company to delete.'
        }
    ],
    'responses': {
        '204': {'description': 'Company deleted successfully'},
        '404': {'description': 'Company not found'}
    }
})
def delete_company(company_id: int):
    db: Session = get_db()
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    company.delete(db)
    return 'message: Company deleted successfully', 204
