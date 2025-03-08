from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from datetime import datetime

class FeedbackForm(db.Model):
    """Feedback form model"""
    id = db.Column(db.Integer, primary_key=True)
    form_field = db.Column(MutableDict.as_mutable(JSON), nullable=True)  # to store feedback questions
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref='feedback_forms')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref='feedback_forms')
    instance_id = db.Column(db.Integer, db.ForeignKey('feedback_instance.id'), nullable=True)
    instance = db.relationship('FeedbackInstance', backref='feedback_forms')
    due_date = db.Column(db.DateTime, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    batch_list = db.Column(MutableDict.as_mutable(JSON), nullable=True)
    is_theory = db.Column(db.Boolean, default=True)
    is_alive = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'{self.id}'

class FeedbackUserConnector(db.Model):
    """Connector between user and feedback form"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('User', backref='feedback_connectors')
    is_filled = db.Column(db.Boolean, default=False)
    user_feedback = db.Column(MutableDict.as_mutable(JSON), nullable=True)  # to store feedback user data
    form_id = db.Column(db.Integer, db.ForeignKey('feedback_form.id'), nullable=False)
    form = db.relationship('FeedbackForm', backref='user_connectors')
    
    def __repr__(self):
        return f'{self.id}-> id || {self.student.email}->Student' 