from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
import os

def check_authorization():
    """Check if the request has a valid JWT token"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            return user
        return None
    except Exception:
        return None

def basic_auth(f):
    """Decorator to check for basic authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = check_authorization()
        if user:
            request.current_user = user
            return f(*args, **kwargs)
        return jsonify({"status_code": 403, "status_msg": "Access denied, Authentication header not found or invalid token"}), 403
    return decorated

def superuser_auth(f):
    """Decorator to check for superuser authentication"""
    @wraps(f)
    @basic_auth
    def decorated(*args, **kwargs):
        if request.current_user.is_superuser:
            request.current_admin = request.current_user
            return f(*args, **kwargs)
        return jsonify({"status_code": 400, "status_msg": "User is not authorized to perform this action"}), 400
    return decorated

def teacher_auth(f):
    """Decorator to check for teacher authentication"""
    @wraps(f)
    @basic_auth
    def decorated(*args, **kwargs):
        if request.current_user.is_staff:
            request.current_teacher = request.current_user
            return f(*args, **kwargs)
        return jsonify({"status_code": 400, "status_msg": "User is not authorized to perform this action"}), 400
    return decorated 