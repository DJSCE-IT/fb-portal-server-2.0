from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User, MyUser
from app.utils.auth import basic_auth, teacher_auth, superuser_auth

user_bp = Blueprint('user', __name__)

@user_bp.route('/getProfile', methods=['GET'])
@basic_auth
def get_profile():
    """Get the current user's profile"""
    try:
        my_user = MyUser.query.filter_by(user=request.current_user).first()
        
        if not my_user:
            return jsonify({"status_code": 404, "status_msg": "User profile not found"}), 404
        
        profile_data = {
            "name": my_user.name,
            "email": my_user.email,
            "age": my_user.age,
            "gender": my_user.gender,
            "sapId": my_user.sapId,
            "mobile": my_user.mobile,
            "year": my_user.year,
            "is_staff": request.current_user.is_staff,
            "is_superuser": request.current_user.is_superuser,
            "canCreateBatch": my_user.canCreateBatch,
            "canCreateSubject": my_user.canCreateSubject,
            "canCreateFeedbackForm": my_user.canCreateFeedbackForm
        }
        
        return jsonify({
            "status_code": 200,
            "data": profile_data
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@user_bp.route('/saveProfile', methods=['POST'])
@basic_auth
def save_profile():
    """Update the current user's profile"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    try:
        my_user = MyUser.query.filter_by(user=request.current_user).first()
        
        if not my_user:
            return jsonify({"status_code": 404, "status_msg": "User profile not found"}), 404
        
        # Update profile fields
        if 'name' in data:
            my_user.name = data['name']
        
        if 'age' in data:
            my_user.age = data['age']
        
        if 'gender' in data:
            my_user.gender = data['gender']
        
        if 'sapId' in data:
            my_user.sapId = data['sapId']
        
        if 'mobile' in data:
            my_user.mobile = data['mobile']
        
        if 'year' in data:
            my_user.year = data['year']
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Profile updated successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@user_bp.route('/getTUsers/<string:username>', methods=['GET'])
@basic_auth
def get_t_users(username):
    """Get teacher user details"""
    try:
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.is_staff:
            return jsonify({"status_code": 404, "status_msg": "Teacher not found"}), 404
        
        my_user = MyUser.query.filter_by(user=user).first()
        
        if not my_user:
            return jsonify({"status_code": 404, "status_msg": "Teacher profile not found"}), 404
        
        user_data = {
            "email": my_user.email,
            "id": user.id,
            "name": my_user.name,
            "is_staff": user.is_staff
        }
        
        return jsonify({
            "status_code": 200,
            "data": user_data
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@user_bp.route('/gettUsersBac/<string:username>', methods=['GET'])
@basic_auth
def get_t_users_bac(username):
    """Get teacher user details (backward compatibility)"""
    return get_t_users(username)

@user_bp.route('/getuserslist', methods=['GET'])
@basic_auth
def get_users_list():
    """Get a list of all users"""
    try:
        users = User.query.all()
        
        result = []
        for user in users:
            my_user = MyUser.query.filter_by(user=user).first()
            
            if my_user:
                user_data = {
                    "email": my_user.email,
                    "id": user.id,
                    "is_staff": user.is_staff,
                    "name": my_user.name
                }
                result.append(user_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@user_bp.route('/tSettings', methods=['POST'])
@basic_auth
@superuser_auth
def t_settings():
    """Update teacher permissions"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status_code": 400, "status_msg": "Missing user ID"}), 400
    
    try:
        user = User.query.get(user_id)
        
        if not user or not user.is_staff:
            return jsonify({"status_code": 404, "status_msg": "Teacher not found"}), 404
        
        my_user = MyUser.query.filter_by(user=user).first()
        
        if not my_user:
            return jsonify({"status_code": 404, "status_msg": "Teacher profile not found"}), 404
        
        # Update permissions
        if 'canCreateBatch' in data:
            my_user.canCreateBatch = data['canCreateBatch']
        
        if 'canCreateSubject' in data:
            my_user.canCreateSubject = data['canCreateSubject']
        
        if 'canCreateFeedbackForm' in data:
            my_user.canCreateFeedbackForm = data['canCreateFeedbackForm']
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Teacher permissions updated successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500 