from flask import Blueprint, request, jsonify
from app import db
from app.models.subject import Subject, SubjectTheory, SubjectPractical
from app.models.instance import FeedbackInstance
from app.models.batch import Batch
from app.models.user import User, MyUser
from app.utils.auth import basic_auth, teacher_auth, superuser_auth

subject_bp = Blueprint('subject', __name__)

@subject_bp.route('/getallsubjects', methods=['GET'])
@basic_auth
def get_all_subjects():
    """Get all subjects with optional instance filtering"""
    instance_id = request.args.get('instance_id')
    
    try:
        query = Subject.query
        
        if instance_id:
            query = query.filter_by(instance_id=instance_id)
        
        subjects = query.all()
        
        result = []
        for subject in subjects:
            # Get theory subjects
            theory_subjects = SubjectTheory.query.filter_by(subject=subject).all()
            theory_data = []
            
            for theory in theory_subjects:
                batch = theory.batch
                teacher_ids = theory.sub_teacher_email
                teachers = []
                
                for teacher_id in teacher_ids:
                    user = User.query.get(teacher_id)
                    if user and hasattr(user, 'myuser'):
                        teachers.append(user.myuser.name)
                
                theory_data.append({
                    "id": theory.id,
                    "subject_name": subject.subject_name,
                    "batch_id": batch.id,
                    "batch_name": batch.batch_name,
                    "batch_year": batch.year,
                    "sub_teacher_name": teachers
                })
            
            # Get practical subjects
            practical_subjects = SubjectPractical.query.filter_by(subject=subject).all()
            practical_data = []
            
            for practical in practical_subjects:
                batch = practical.batch
                teacher_ids = practical.prac_teacher_email
                teachers = []
                
                for teacher_id in teacher_ids:
                    user = User.query.get(teacher_id)
                    if user and hasattr(user, 'myuser'):
                        teachers.append(user.myuser.name)
                
                practical_data.append({
                    "id": practical.id,
                    "subject_name": subject.subject_name,
                    "batch_id": batch.id,
                    "batch_name": batch.batch_name,
                    "batch_year": batch.year,
                    "prac_teacher_name": teachers
                })
            
            subject_data = {
                "id": subject.id,
                "subject_name": subject.subject_name,
                "instance_name": subject.instance.instance_name if subject.instance else None,
                "is_selected": subject.instance.is_selected if subject.instance else False,
                "theory_subject": theory_data,
                "practical_subject": practical_data
            }
            
            result.append(subject_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@subject_bp.route('/deletesubject/<int:subject_id>/', methods=['DELETE'])
@basic_auth
@teacher_auth
def delete_subject(subject_id):
    """Delete a subject"""
    try:
        subject = Subject.query.get(subject_id)
        
        if not subject:
            return jsonify({"status_code": 404, "status_msg": "Subject not found"}), 404
        
        # Delete all theory subjects
        SubjectTheory.query.filter_by(subject=subject).delete()
        
        # Delete all practical subjects
        SubjectPractical.query.filter_by(subject=subject).delete()
        
        # Delete the subject
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Subject deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@subject_bp.route('/addTheorySubject', methods=['POST'])
@basic_auth
@teacher_auth
def add_theory_subject():
    """Add a theory subject"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    try:
        # Extract data
        subject_name = data.get('subject_name')
        batch_id = data.get('batch_id')
        teacher_ids = data.get('teacher_ids', [])
        instance_id = data.get('instance_id')
        
        # Validate data
        if not subject_name or not batch_id or not teacher_ids:
            return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400
        
        # Check if batch exists
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({"status_code": 404, "status_msg": "Batch not found"}), 404
        
        # Check if instance exists if provided
        instance = None
        if instance_id:
            instance = FeedbackInstance.query.get(instance_id)
            if not instance:
                return jsonify({"status_code": 404, "status_msg": "Instance not found"}), 404
        
        # Create or get subject
        subject = Subject.query.filter_by(subject_name=subject_name, instance=instance).first()
        if not subject:
            subject = Subject(subject_name=subject_name, instance=instance)
            db.session.add(subject)
            db.session.flush()
        
        # Create theory subject
        theory_subject = SubjectTheory(
            subject=subject,
            batch=batch,
            sub_teacher_email=teacher_ids
        )
        
        db.session.add(theory_subject)
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Theory subject added successfully",
            "subject_id": subject.id,
            "theory_id": theory_subject.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@subject_bp.route('/addPractical', methods=['POST'])
@basic_auth
@teacher_auth
def add_practical_subject():
    """Add a practical subject"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    try:
        # Extract data
        subject_name = data.get('subject_name')
        batch_id = data.get('batch_id')
        teacher_ids = data.get('teacher_ids', [])
        instance_id = data.get('instance_id')
        
        # Validate data
        if not subject_name or not batch_id or not teacher_ids:
            return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400
        
        # Check if batch exists
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({"status_code": 404, "status_msg": "Batch not found"}), 404
        
        # Check if instance exists if provided
        instance = None
        if instance_id:
            instance = FeedbackInstance.query.get(instance_id)
            if not instance:
                return jsonify({"status_code": 404, "status_msg": "Instance not found"}), 404
        
        # Create or get subject
        subject = Subject.query.filter_by(subject_name=subject_name, instance=instance).first()
        if not subject:
            subject = Subject(subject_name=subject_name, instance=instance)
            db.session.add(subject)
            db.session.flush()
        
        # Create practical subject
        practical_subject = SubjectPractical(
            subject=subject,
            batch=batch,
            prac_teacher_email=teacher_ids
        )
        
        db.session.add(practical_subject)
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Practical subject added successfully",
            "subject_id": subject.id,
            "practical_id": practical_subject.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500 