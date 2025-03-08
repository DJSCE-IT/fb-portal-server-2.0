from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.feedback import FeedbackForm, FeedbackUserConnector
from app.models.user import User, MyUser
from app.models.subject import Subject
from app.models.batch import Batch
from app.models.instance import FeedbackInstance
from app.utils.auth import basic_auth, teacher_auth
from app.utils.email import send_feedback_reminder

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/createFeedbackForm', methods=['POST'])
@basic_auth
def create_feedback_form():
    """Create a new feedback form"""
    if not request.current_user.is_staff:
        return jsonify({"status_code": 403, "status_msg": "Permission denied"}), 403
    
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    try:
        # Extract form data
        form_field = data.get('form_field', {})
        subject_id = data.get('subject_id')
        instance_id = data.get('instance_id')
        due_date = data.get('due_date')
        year = data.get('year')
        batch_list = data.get('batch_list', [])
        is_theory = data.get('is_theory', True)
        
        # Validate data
        if not subject_id or not due_date or not year:
            return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400
        
        # Convert due_date string to datetime
        try:
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"status_code": 400, "status_msg": "Invalid date format"}), 400
        
        # Check if subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"status_code": 404, "status_msg": "Subject not found"}), 404
        
        # Check if instance exists if provided
        instance = None
        if instance_id:
            instance = FeedbackInstance.query.get(instance_id)
            if not instance:
                return jsonify({"status_code": 404, "status_msg": "Instance not found"}), 404
        
        # Create feedback form
        new_form = FeedbackForm(
            form_field=form_field,
            teacher=request.current_user,
            subject=subject,
            instance=instance,
            due_date=due_date,
            year=year,
            batch_list=batch_list,
            is_theory=is_theory,
            is_alive=True
        )
        
        db.session.add(new_form)
        db.session.flush()  # To get the form ID
        
        # Create connectors for students in the batches
        if batch_list:
            for batch_id in batch_list:
                batch = Batch.query.get(batch_id)
                if batch:
                    for student in batch.student_email_mtm:
                        user = User.query.filter_by(email=student.email).first()
                        if user:
                            connector = FeedbackUserConnector(
                                student=user,
                                is_filled=False,
                                form=new_form
                            )
                            db.session.add(connector)
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Feedback form created successfully",
            "form_id": new_form.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/updateFeedbackform', methods=['POST'])
@basic_auth
def update_feedback_form():
    """Update an existing feedback form"""
    if not request.current_user.is_staff:
        return jsonify({"status_code": 403, "status_msg": "Permission denied"}), 403
    
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    form_id = data.get('form_id')
    
    if not form_id:
        return jsonify({"status_code": 400, "status_msg": "Missing form ID"}), 400
    
    try:
        form = FeedbackForm.query.get(form_id)
        
        if not form:
            return jsonify({"status_code": 404, "status_msg": "Feedback form not found"}), 404
        
        # Update form fields
        if 'form_field' in data:
            form.form_field = data['form_field']
        
        if 'subject_id' in data:
            subject = Subject.query.get(data['subject_id'])
            if subject:
                form.subject = subject
        
        if 'instance_id' in data:
            instance = FeedbackInstance.query.get(data['instance_id'])
            if instance:
                form.instance = instance
        
        if 'due_date' in data:
            try:
                form.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"status_code": 400, "status_msg": "Invalid date format"}), 400
        
        if 'year' in data:
            form.year = data['year']
        
        if 'batch_list' in data:
            old_batch_list = form.batch_list or []
            new_batch_list = data['batch_list']
            form.batch_list = new_batch_list
            
            # Add new connectors for new batches
            for batch_id in new_batch_list:
                if batch_id not in old_batch_list:
                    batch = Batch.query.get(batch_id)
                    if batch:
                        for student in batch.student_email_mtm:
                            user = User.query.filter_by(email=student.email).first()
                            if user:
                                # Check if connector already exists
                                existing = FeedbackUserConnector.query.filter_by(
                                    student=user, form=form
                                ).first()
                                
                                if not existing:
                                    connector = FeedbackUserConnector(
                                        student=user,
                                        is_filled=False,
                                        form=form
                                    )
                                    db.session.add(connector)
            
            # Remove connectors for removed batches
            for batch_id in old_batch_list:
                if batch_id not in new_batch_list:
                    batch = Batch.query.get(batch_id)
                    if batch:
                        for student in batch.student_email_mtm:
                            user = User.query.filter_by(email=student.email).first()
                            if user:
                                connector = FeedbackUserConnector.query.filter_by(
                                    student=user, form=form
                                ).first()
                                
                                if connector:
                                    db.session.delete(connector)
        
        if 'is_theory' in data:
            form.is_theory = data['is_theory']
        
        if 'is_alive' in data:
            form.is_alive = data['is_alive']
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Feedback form updated successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/deleteFeedbackform', methods=['POST'])
@basic_auth
def delete_feedback_form():
    """Delete a feedback form"""
    if not request.current_user.is_staff:
        return jsonify({"status_code": 403, "status_msg": "Permission denied"}), 403
    
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json
    form_id = data.get('form_id')
    
    if not form_id:
        return jsonify({"status_code": 400, "status_msg": "Missing form ID"}), 400
    
    try:
        form = FeedbackForm.query.get(form_id)
        
        if not form:
            return jsonify({"status_code": 404, "status_msg": "Feedback form not found"}), 404
        
        # Delete all connectors first
        FeedbackUserConnector.query.filter_by(form=form).delete()
        
        # Delete the form
        db.session.delete(form)
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Feedback form deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/getFeedbackForm', methods=['GET'])
@basic_auth
def get_feedback_form():
    """Get feedback forms with optional filtering"""
    instance_id = request.args.get('instance_id')
    
    try:
        query = FeedbackForm.query
        
        if instance_id:
            query = query.filter_by(instance_id=instance_id)
        
        forms = query.all()
        
        result = []
        for form in forms:
            form_data = {
                "id": form.id,
                "subject_name": form.subject.subject_name,
                "is_alive": form.is_alive,
                "is_theory": form.is_theory,
                "year": form.year,
                "due_date": form.due_date.isoformat(),
                "batch_list": form.batch_list,
                "is_selected": form.instance.is_selected if form.instance else False
            }
            result.append(form_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/getFeedbackData', methods=['GET'])
@basic_auth
def get_feedback_data():
    """Get detailed feedback data for a specific form"""
    form_id = request.args.get('form_id')
    
    if not form_id:
        return jsonify({"status_code": 400, "status_msg": "Missing form ID"}), 400
    
    try:
        form = FeedbackForm.query.get(form_id)
        
        if not form:
            return jsonify({"status_code": 404, "status_msg": "Feedback form not found"}), 404
        
        connectors = FeedbackUserConnector.query.filter_by(form=form).all()
        
        result = []
        for connector in connectors:
            student = connector.student
            my_user = MyUser.query.filter_by(user=student).first()
            
            if my_user:
                connector_data = {
                    "student": student.username,
                    "student_name": my_user.name,
                    "is_filled": connector.is_filled,
                    "user_feedback": connector.user_feedback,
                    "teacher_name": form.teacher.myuser.name,
                    "teacher_email": form.teacher.username,
                    "subject": form.subject.subject_name,
                    "due_date": form.due_date.isoformat(),
                    "year": form.year,
                    "is_theory": form.is_theory,
                    "is_alive": form.is_alive,
                    "subject_id": form.subject.id,
                    "form_id": form.id
                }
                result.append(connector_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/saveFeedbackFormResult', methods=['POST'])
@basic_auth
def save_feedback_form_result():
    """Save feedback form result submitted by a student"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json.get('data', {})
    form_id = data.get('form_id')
    feedback_data = data.get('form_data', {})
    
    if not form_id or not feedback_data:
        return jsonify({"status_code": 400, "status_msg": "Missing required fields"}), 400
    
    try:
        # Find the connector
        connector = FeedbackUserConnector.query.filter_by(
            form_id=form_id, student=request.current_user
        ).first()
        
        if not connector:
            return jsonify({"status_code": 404, "status_msg": "Feedback form not found for this user"}), 404
        
        # Save the feedback data
        connector.user_feedback = feedback_data
        connector.is_filled = True
        
        db.session.commit()
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Feedback submitted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/sendReminder', methods=['POST'])
@basic_auth
@teacher_auth
def send_reminder():
    """Send reminder emails to students who haven't filled the feedback form"""
    if not request.is_json:
        return jsonify({"status_code": 400, "status_msg": "Missing JSON in request"}), 400
    
    data = request.json.get('data', {})
    form_id = data.get('form_id')
    
    if not form_id:
        return jsonify({"status_code": 400, "status_msg": "Missing form ID"}), 400
    
    try:
        form = FeedbackForm.query.get(form_id)
        
        if not form:
            return jsonify({"status_code": 404, "status_msg": "Feedback form not found"}), 404
        
        # Get connectors for students who haven't filled the form
        unfilled_connectors = FeedbackUserConnector.query.filter_by(
            form=form, is_filled=False
        ).all()
        
        if not unfilled_connectors:
            return jsonify({
                "status_code": 200,
                "status_msg": "No reminders needed, all students have filled the form"
            }), 200
        
        # Get the list of email addresses
        email_list = [connector.student.email for connector in unfilled_connectors]
        
        # Send reminder emails
        send_feedback_reminder(email_list, form)
        
        return jsonify({
            "status_code": 200,
            "status_msg": "Reminder emails sent successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/getSDashData', methods=['GET'])
@basic_auth
def get_s_dash_data():
    """Get dashboard data for student"""
    try:
        # Get active forms for the current student
        connectors = FeedbackUserConnector.query.filter_by(
            student=request.current_user, is_filled=False
        ).join(FeedbackForm).filter_by(is_alive=True).all()
        
        result = []
        for connector in connectors:
            form = connector.form
            form_data = {
                "subject": form.subject.subject_name,
                "is_filled": connector.is_filled,
                "teacher_name": form.teacher.myuser.name,
                "due_date": form.due_date.isoformat(),
                "year": form.year,
                "is_theory": form.is_theory,
                "is_alive": form.is_alive,
                "form_id": form.id,
                "subject_id": form.subject.id
            }
            result.append(form_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/getSDashDataFilled', methods=['GET'])
@basic_auth
def get_s_dash_data_filled():
    """Get filled feedback data for student dashboard"""
    try:
        # Get forms filled by the current student
        connectors = FeedbackUserConnector.query.filter_by(
            student=request.current_user, is_filled=True
        ).all()
        
        result = []
        for connector in connectors:
            form = connector.form
            form_data = {
                "subject": form.subject.subject_name,
                "is_filled": connector.is_filled,
                "teacher_name": form.teacher.myuser.name,
                "due_date": form.due_date.isoformat(),
                "year": form.year,
                "is_theory": form.is_theory,
                "is_alive": form.is_alive,
                "form_id": form.id,
                "subject_id": form.subject.id
            }
            result.append(form_data)
        
        return jsonify({
            "status_code": 200,
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500

@feedback_bp.route('/getSDashDataForm', methods=['GET'])
@basic_auth
def get_s_dash_data_form():
    """Get specific form data for student dashboard"""
    form_id = request.args.get('form_id')
    
    if not form_id:
        return jsonify({"status_code": 400, "status_msg": "Missing form ID"}), 400
    
    try:
        # Get the form
        form = FeedbackForm.query.get(form_id)
        
        if not form:
            return jsonify({"status_code": 404, "status_msg": "Feedback form not found"}), 404
        
        # Get the connector for the current student
        connector = FeedbackUserConnector.query.filter_by(
            form=form, student=request.current_user
        ).first()
        
        if not connector:
            return jsonify({"status_code": 404, "status_msg": "Form not assigned to this student"}), 404
        
        form_data = {
            "form_field": form.form_field,
            "subject": form.subject.subject_name,
            "is_filled": connector.is_filled,
            "user_feedback": connector.user_feedback,
            "teacher_name": form.teacher.myuser.name,
            "due_date": form.due_date.isoformat(),
            "year": form.year,
            "is_theory": form.is_theory,
            "is_alive": form.is_alive,
            "form_id": form.id,
            "subject_id": form.subject.id
        }
        
        return jsonify({
            "status_code": 200,
            "data": form_data
        }), 200
    
    except Exception as e:
        return jsonify({"status_code": 500, "status_msg": str(e)}), 500 