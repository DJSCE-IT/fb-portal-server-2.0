from flask import Blueprint, jsonify
from api.routes.auth import token_required

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({
        'message': 'Welcome to the Flask API',
        'version': 'v1.0',
        'status': 'running'
    })

@bp.route('/protected')
@token_required
def protected(current_user):
    return jsonify({
        'message': f'Hello {current_user.username}! This is a protected route.',
        'user_id': current_user.id
    }) 