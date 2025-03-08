from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import string
import random
from datetime import datetime, timedelta
from app import db
from app.models.user import User, MyUser
from app.models.otp import Otp
from app.utils.auth import basic_auth, teacher_auth, superuser_auth
from app.utils.email import send_otp_email, send_reset_password_email

auth_bp = Blueprint('auth', __name__)

def get_tokens_for_user(user):
    """Generate access and refresh tokens for the user"""
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return {
        'access': access_token,
        'refresh': refresh_token
    }

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Generate a random string of fixed length"""
    return ''.join(random.choice(chars) for _ in range(size))

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user with email and password"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    email = data.get('email', None)
    password = data.get('password', None)

    if not email or not password:
        return jsonify({"status_code": 400, "status_msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({"status_code": 401, "status_msg": "Invalid email or password"}), 401

    if not user.check_password(password):
        return jsonify({"status_code": 401, "status_msg": "Invalid email or password"}), 401

    try:
        my_user = MyUser.query.filter_by(email=email).first()
        
        if not my_user.isVerified:
            return jsonify({
                "status_code": 403,
                "status_msg": "Please complete authentication",
                "email": email
            }), 403
            
        tokens = get_tokens_for_user(user)
        
        # Check if user is a teacher/admin
        if user.is_staff:
            return jsonify({
                "status_code": 200,
                "status_msg": "Login Successful",
                "tokens": tokens,
                "is_teacher": True,
                "is_superuser": user.is_superuser,
                "name": my_user.name,
                "email": my_user.email,
                "canCreateBatch": my_user.canCreateBatch,
                "canCreateSubject": my_user.canCreateSubject,
                "canCreateFeedbackForm": my_user.canCreateFeedbackForm
            }), 200
        else:
            # Student login
            return jsonify({
                "status_code": 200,
                "status_msg": "Login Successful",
                "tokens": tokens,
                "is_teacher": False,
                "name": my_user.name,
                "email": my_user.email
            }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@auth_bp.route('/sendOtp', methods=['POST'])
def send_otp():
    """Send OTP to user's email for verification"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    email = data.get('email', None)

    if not email:
        return jsonify({"status_code": 400, "status_msg": "Missing email"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({"status_code": 404, "status_msg": "User not found"}), 404
    
    try:
        # Generate a new OTP
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
        
        # Store the OTP in the database
        existing_otp = Otp.query.filter_by(LoginUser=user).first()
        if existing_otp:
            existing_otp.Otp = otp
            existing_otp.timeOfGeneration = datetime.utcnow()
        else:
            new_otp = Otp(Otp=otp, LoginUser=user)
            db.session.add(new_otp)
        
        db.session.commit()
        
        # Send the OTP via email
        send_otp_email(email, otp)
        
        return jsonify({"status_code": 200, "status_msg": "OTP sent successfully"}), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@auth_bp.route('/verifyOtp', methods=['POST'])
def verify_otp():
    """Verify OTP entered by the user"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    email = data.get('email', None)
    otp = data.get('otp', None)

    if not email or not otp:
        return jsonify({"status_code": 400, "status_msg": "Missing email or OTP"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({"status_code": 404, "status_msg": "User not found"}), 404
    
    try:
        stored_otp = Otp.query.filter_by(LoginUser=user).first()
        
        if not stored_otp:
            return jsonify({"status_code": 404, "status_msg": "OTP not found"}), 404
        
        # Check if OTP is expired (10 minutes validity)
        time_diff = datetime.utcnow() - stored_otp.timeOfGeneration
        if time_diff > timedelta(minutes=10):
            return jsonify({"status_code": 400, "status_msg": "OTP expired"}), 400
        
        # Verify OTP
        if stored_otp.Otp != otp:
            return jsonify({"status_code": 400, "status_msg": "Invalid OTP"}), 400
        
        # Mark user as verified
        my_user = MyUser.query.filter_by(email=email).first()
        my_user.isVerified = True
        db.session.commit()
        
        # Generate tokens
        tokens = get_tokens_for_user(user)
        
        # Check if user is a teacher/admin
        if user.is_staff:
            return jsonify({
                "status_code": 200,
                "status_msg": "Login Successful",
                "tokens": tokens,
                "is_teacher": True,
                "is_superuser": user.is_superuser,
                "name": my_user.name,
                "email": my_user.email,
                "canCreateBatch": my_user.canCreateBatch,
                "canCreateSubject": my_user.canCreateSubject,
                "canCreateFeedbackForm": my_user.canCreateFeedbackForm
            }), 200
        else:
            # Student login
            return jsonify({
                "status_code": 200,
                "status_msg": "Login Successful",
                "tokens": tokens,
                "is_teacher": False,
                "name": my_user.name,
                "email": my_user.email
            }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@auth_bp.route('/resetPasswordMail', methods=['POST'])
def reset_password_mail():
    """Send reset password mail to the user"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    email = data.get('email', None)

    if not email:
        return jsonify({"status_code": 400, "status_msg": "Missing email"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({"status_code": 404, "status_msg": "User not found"}), 404
    
    try:
        # Generate a token
        token = id_generator()
        
        # Store the token in the user's profile
        my_user = MyUser.query.filter_by(email=email).first()
        my_user.passChangeToken = token
        db.session.commit()
        
        # Send reset password email
        send_reset_password_email(email, token)
        
        return jsonify({"status_code": 200, "status_msg": "Reset password mail sent successfully"}), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@auth_bp.route('/getPass', methods=['POST'])
def get_pass():
    """Verify reset password token"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    email = data.get('email', None)
    token = data.get('pass', None)

    if not email or not token:
        return jsonify({"status_code": 400, "status_msg": "Missing email or token"}), 400

    my_user = MyUser.query.filter_by(email=email).first()
    
    if my_user is None or my_user.passChangeToken != token:
        return jsonify({"status_code": 400, "status_msg": "Invalid token"}), 400
    
    return jsonify({"status_code": 200, "status_msg": "Token verified successfully"}), 200

@auth_bp.route('/resetPassword', methods=['POST'])
def reset_password():
    """Reset user's password"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    email = data.get('email', None)
    token = data.get('pass', None)
    new_password = data.get('new_pass', None)

    if not email or not token or not new_password:
        return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400

    user = User.query.filter_by(email=email).first()
    my_user = MyUser.query.filter_by(email=email).first()
    
    if user is None or my_user is None or my_user.passChangeToken != token:
        return jsonify({"status_code": 400, "status_msg": "Invalid token or user"}), 400
    
    try:
        # Update password
        user.set_password(new_password)
        
        # Clear the token
        my_user.passChangeToken = None
        
        db.session.commit()
        
        return jsonify({"status_code": 200, "status_msg": "Password reset successfully"}), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@auth_bp.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token using refresh token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"status_code": 404, "status_msg": "User not found"}), 404
    
    # Generate new access token
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({"access": access_token}), 200

@auth_bp.route('/createTeacher', methods=['POST'])
def create_teacher():
    """Create a new teacher account"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400

    data = request.json
    secret_code = data.get('secret_code', None)
    
    # Check if secret code matches with the one in database
    # Here, you would check against your MetaInfo table
    
    email = data.get('email', None)
    password = data.get('password', None)
    name = data.get('name', None)
    
    if not email or not password or not name:
        return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"status_code": 400, "status_msg": "User already exists"}), 400
    
    try:
        # Create new user
        new_user = User(
            username=email,
            email=email,
            is_staff=True,
            is_superuser=False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Get the user ID
        
        # Create MyUser profile
        new_my_user = MyUser(
            email=email,
            user=new_user,
            name=name,
            isVerified=False
        )
        db.session.add(new_my_user)
        db.session.commit()
        
        return jsonify({"status_code": 200, "status_msg": "Teacher account created successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@auth_bp.route('/getAllTeacherMails', methods=['GET'])
@basic_auth
def get_all_staff_emails():
    """Get a list of all teacher emails"""
    users = User.query.filter_by(is_staff=True).all()
    emails = [user.email for user in users]
    
    return jsonify({"status_code": 200, "data": emails}), 200

@auth_bp.route('/test', methods=['GET'])
@superuser_auth
def test():
    """Test endpoint for superuser authentication"""
    return jsonify({"status_code": 200, "status_msg": "Superuser authentication works!"}), 200 