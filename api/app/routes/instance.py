from flask import Blueprint, request, jsonify
import string
import random
from app import db
from app.models.instance import FeedbackInstance, MetaInfo
from app.utils.auth import basic_auth, teacher_auth, superuser_auth

instance_bp = Blueprint('instance', __name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Generate a random string of fixed length"""
    return ''.join(random.choice(chars) for _ in range(size))

@instance_bp.route('/createNewInst', methods=['POST'])
@basic_auth
@superuser_auth
def create_new_instance():
    """Create a new feedback instance"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    instance_name = data.get('instance_name')
    
    if not instance_name:
        return jsonify({"status_code": 400, "status_msg": "Missing instance name"}), 400
    
    try:
        # Check if an instance with the same name already exists
        existing_instance = FeedbackInstance.query.filter_by(instance_name=instance_name).first()
        if existing_instance:
            return jsonify({"status_code": 400, "status_msg": "Instance with this name already exists"}), 400
        
        # Get the current latest instance
        latest_instance = FeedbackInstance.query.filter_by(is_latest=True).first()
        
        # Create new instance
        new_instance = FeedbackInstance(
            instance_name=instance_name,
            is_latest=True,
            is_selected=True
        )
        
        db.session.add(new_instance)
        
        # Update the previous latest instance
        if latest_instance:
            latest_instance.is_latest = False
            
            # If the previous latest was also selected, deselect it
            if latest_instance.is_selected:
                latest_instance.is_selected = False
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Instance created successfully",
            "instance_id": new_instance.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@instance_bp.route('/generateSecretCode', methods=['POST'])
@basic_auth
@superuser_auth
def generate_secret_code():
    """Generate a new secret code for teacher registration"""
    try:
        # Generate a new secret code
        secret_code = id_generator(8)
        
        # Get the current meta info or create a new one
        meta_info = MetaInfo.query.first()
        if not meta_info:
            meta_info = MetaInfo(secret_code=secret_code)
            db.session.add(meta_info)
        else:
            meta_info.secret_code = secret_code
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Secret code generated successfully",
            "secret_code": secret_code
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500 