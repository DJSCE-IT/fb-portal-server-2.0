from flask import Blueprint, jsonify, request
from api.models.user import User
from api.routes.auth import token_required
from datetime import datetime

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    user_dict = current_user.to_dict()
    user_dict['_id'] = str(user_dict['_id'])
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
    return jsonify(user_dict)

@bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    
    if 'username' in data and data['username'] != current_user.username:
        if User.find_by_username(data['username']):
            return jsonify({'message': 'Username already taken'}), 400
        current_user.username = data['username']
    
    if 'email' in data and data['email'] != current_user.email:
        if User.find_by_email(data['email']):
            return jsonify({'message': 'Email already registered'}), 400
        current_user.email = data['email']
    
    current_user.updated_at = datetime.utcnow()
    current_user.save()
    
    user_dict = current_user.to_dict()
    user_dict['_id'] = str(user_dict['_id'])
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
    return jsonify(user_dict)

@bp.route('/profile', methods=['DELETE'])
@token_required
def delete_profile(current_user):
    current_user.delete()
    return jsonify({'message': 'User deleted successfully'}) 