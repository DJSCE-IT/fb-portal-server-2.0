from flask import Blueprint, request, jsonify
from api.models.user import User
import jwt
from datetime import datetime, timedelta
from functools import wraps
from api.config.config import Config
from bson import ObjectId, json_util
import json

bp = Blueprint('auth', __name__, url_prefix='/auth')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = User.find_by_id(data['user_id'])
            if not current_user:
                raise Exception('User not found')
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    if User.find_by_email(data['email']):
        return jsonify({'message': 'Email already registered'}), 400
        
    if User.find_by_username(data['username']):
        return jsonify({'message': 'Username already taken'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    user.save()
    
    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    user = User.find_by_email(data['email'])
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    token = jwt.encode({
        'user_id': str(user._id),
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, Config.JWT_SECRET_KEY)
    
    # Convert ObjectId to string for JSON serialization
    user_dict = user.to_dict()
    user_dict['_id'] = str(user_dict['_id'])
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['updated_at'] = user_dict['updated_at'].isoformat()
    
    return jsonify({
        'token': token,
        'user': user_dict
    }) 