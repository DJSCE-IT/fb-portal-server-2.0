from flask import Blueprint, request, jsonify
from app import db
from app.models.batch import Batch
from app.models.user import User, MyUser
from app.models.instance import FeedbackInstance
from app.utils.auth import basic_auth, teacher_auth, superuser_auth

batch_bp = Blueprint('batch', __name__)

@batch_bp.route('/getBatches', methods=['GET'])
@basic_auth
def get_batches():
    """Get all batches with optional instance filtering"""
    instance_id = request.args.get('instance_id')
    
    try:
        query = Batch.query
        
        if instance_id:
            query = query.filter_by(instance_id=instance_id)
        
        batches = query.all()
        
        result = []
        for batch in batches:
            batch_data = {
                "label": batch.batch_name,
                "value": batch.id,
                "year": batch.year
            }
            result.append(batch_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@batch_bp.route('/getYrBatches', methods=['GET'])
@basic_auth
def get_yr_batches():
    """Get batches for a specific year"""
    year = request.args.get('year')
    instance_id = request.args.get('instance_id')
    
    if not year:
        return jsonify({"status_code": 400, "status_msg": "Missing year parameter"}), 400
    
    try:
        query = Batch.query.filter_by(year=year)
        
        if instance_id:
            query = query.filter_by(instance_id=instance_id)
        
        batches = query.all()
        
        result = []
        for batch in batches:
            batch_data = {
                "label": batch.batch_name,
                "value": batch.id,
                "year": batch.year
            }
            result.append(batch_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@batch_bp.route('/getYearBatches', methods=['GET'])
@basic_auth
def get_year_batches():
    """Get all years and their batches"""
    instance_id = request.args.get('instance_id')
    
    try:
        query = Batch.query
        
        if instance_id:
            query = query.filter_by(instance_id=instance_id)
        
        # Get distinct years
        years = db.session.query(Batch.year).distinct().all()
        years = [year[0] for year in years]
        
        result = []
        for year in years:
            year_batches = query.filter_by(year=year).all()
            
            batches_data = []
            for batch in year_batches:
                batch_data = {
                    "id": batch.id,
                    "batch_name": batch.batch_name,
                    "batch_division": batch.batch_division,
                    "student_count": len(batch.student_email_mtm)
                }
                batches_data.append(batch_data)
            
            year_data = {
                "year": year,
                "batches": batches_data
            }
            result.append(year_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@batch_bp.route('/bac', methods=['POST'])
@basic_auth
@teacher_auth
def create_batch():
    """Create a new batch"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    try:
        # Extract data
        batch_name = data.get('batch_name')
        batch_division = data.get('batch_division')
        year = data.get('year')
        student_emails = data.get('student_emails', [])
        instance_id = data.get('instance_id')
        
        # Validate data
        if not batch_name or not batch_division or not year:
            return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400
        
        # Check if instance exists if provided
        instance = None
        if instance_id:
            instance = FeedbackInstance.query.get(instance_id)
            if not instance:
                return jsonify({"status_code": 404, "status_msg": "Instance not found"}), 404
        
        # Create batch
        new_batch = Batch(
            batch_name=batch_name,
            batch_division=batch_division,
            year=year,
            student_email={},
            instance=instance
        )
        
        db.session.add(new_batch)
        db.session.flush()  # To get the batch ID
        
        # Add students to batch
        if student_emails:
            for email in student_emails:
                user = User.query.filter_by(email=email).first()
                if user:
                    my_user = MyUser.query.filter_by(email=email).first()
                    if my_user:
                        new_batch.student_email_mtm.append(my_user)
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Batch created successfully",
            "batch_id": new_batch.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@batch_bp.route('/bacUpdate', methods=['POST'])
@basic_auth
@teacher_auth
def update_batch():
    """Update an existing batch"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    batch_id = data.get('batch_id')
    
    if not batch_id:
        return jsonify({"status_code": 400, "status_msg": "Missing batch ID"}), 400
    
    try:
        batch = Batch.query.get(batch_id)
        
        if not batch:
            return jsonify({"status_code": 404, "status_msg": "Batch not found"}), 404
        
        # Update batch fields
        if 'batch_name' in data:
            batch.batch_name = data['batch_name']
        
        if 'batch_division' in data:
            batch.batch_division = data['batch_division']
        
        if 'year' in data:
            batch.year = data['year']
        
        if 'instance_id' in data:
            instance = FeedbackInstance.query.get(data['instance_id'])
            if instance:
                batch.instance = instance
        
        if 'student_emails' in data:
            # Clear existing students
            batch.student_email_mtm.clear()
            
            # Add new students
            for email in data['student_emails']:
                user = User.query.filter_by(email=email).first()
                if user:
                    my_user = MyUser.query.filter_by(email=email).first()
                    if my_user:
                        batch.student_email_mtm.append(my_user)
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Batch updated successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@batch_bp.route('/delBatch', methods=['POST'])
@basic_auth
@teacher_auth
def delete_batch():
    """Delete a batch"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    batch_id = data.get('batch_id')
    
    if not batch_id:
        return jsonify({"status_code": 400, "status_msg": "Missing batch ID"}), 400
    
    try:
        batch = Batch.query.get(batch_id)
        
        if not batch:
            return jsonify({"status_code": 404, "status_msg": "Batch not found"}), 404
        
        # Delete the batch
        db.session.delete(batch)
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Batch deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500 