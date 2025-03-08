from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict

class Subject(db.Model):
    """Subject model"""
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(200), nullable=False)
    instance_id = db.Column(db.Integer, db.ForeignKey('feedback_instance.id'), nullable=True)
    instance = db.relationship('FeedbackInstance', backref='subjects')
    
    def __repr__(self):
        return f'{self.subject_name} subject_name || instance => {self.instance}'

class SubjectTheory(db.Model):
    """Subject theory model"""
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref='theory_subjects')
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    batch = db.relationship('Batch', backref='theory_subjects')
    sub_teacher_email = db.Column(MutableDict.as_mutable(JSON), nullable=False)
    
    def __repr__(self):
        return f'{self.id} id {self.subject.subject_name} subname'

class SubjectPractical(db.Model):
    """Subject practical model"""
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref='practical_subjects')
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    batch = db.relationship('Batch', backref='practical_subjects')
    prac_teacher_email = db.Column(MutableDict.as_mutable(JSON), nullable=False)
    
    def __repr__(self):
        return f'{self.id} id {self.subject.subject_name} prac-subname' 