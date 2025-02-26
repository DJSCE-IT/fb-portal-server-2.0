from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
db = SQLAlchemy(app)

# User model to support MyUser
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)

# Association table for Many-to-Many relationship between Batch and MyUser
batch_student_association = db.Table('batch_student_association',
    db.Column('batch_id', db.Integer, db.ForeignKey('batch.id'), primary_key=True),
    db.Column('myuser_email', db.String(255), db.ForeignKey('myuser.email'), primary_key=True)
)

class MyUser(db.Model, UserMixin):
    email = db.Column(db.String(255), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    sapId = db.Column(db.String(50), nullable=True)
    mobile = db.Column(db.Integer, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    isActivated = db.Column(db.Boolean, default=False)
    passChangeToken = db.Column(db.String(50), nullable=True)
    isVerified = db.Column(db.Boolean, default=False)
    canCreateBatch = db.Column(db.Boolean, default=False)
    canCreateSubject = db.Column(db.Boolean, default=True)
    canCreateFeedbackForm = db.Column(db.Boolean, default=True)

class FeedbackInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance_name = db.Column(db.String(200), nullable=True)
    is_latest = db.Column(db.Boolean, default=False)
    is_selected = db.Column(db.Boolean, default=False)

class MetaInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    secret_code = db.Column(db.String(200), nullable=True)

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(200), nullable=False)
    batch_division = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    student_email = db.Column(db.JSON, nullable=True)
    students = db.relationship('MyUser', secondary=batch_student_association, backref='batches')
    instance_id = db.Column(db.Integer, db.ForeignKey('feedback_instance.id'), nullable=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(200), nullable=False)
    instance_id = db.Column(db.Integer, db.ForeignKey('feedback_instance.id'), nullable=True)

class SubjectTheory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    sub_teacher_email = db.Column(db.JSON, nullable=False)

class SubjectPractical(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    prac_teacher_email = db.Column(db.JSON, nullable=False)

class FeedbackForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_field = db.Column(db.JSON, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    instance_id = db.Column(db.Integer, db.ForeignKey('feedback_instance.id'), nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    batch_list = db.Column(db.JSON, nullable=True)
    is_theory = db.Column(db.Boolean, default=True)
    is_alive = db.Column(db.Boolean, default=True)

class FeedbackUserConnector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_filled = db.Column(db.Boolean, default=False)
    user_feedback = db.Column(db.JSON, nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('feedback_form.id'), nullable=False)

class Otp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    otp = db.Column(db.String(100), nullable=False)
    time_of_generation = db.Column(db.DateTime, default=datetime.utcnow)
    login_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
