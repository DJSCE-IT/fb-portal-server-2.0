from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict

# Association table for many-to-many relationship between Batch and MyUser
batch_student_association = db.Table('batch_student_association',
    db.Column('batch_id', db.Integer, db.ForeignKey('batch.id'), primary_key=True),
    db.Column('myuser_email', db.String(255), db.ForeignKey('my_user.email'), primary_key=True)
)

class Batch(db.Model):
    """Batch model for grouping students"""
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(200), nullable=False)
    batch_division = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    student_email = db.Column(MutableDict.as_mutable(JSON), default={})
    instance_id = db.Column(db.Integer, db.ForeignKey('feedback_instance.id'), nullable=True)
    instance = db.relationship('FeedbackInstance', backref='batches')
    
    # Many-to-many relationship with MyUser
    student_email_mtm = db.relationship('MyUser', secondary=batch_student_association,
                                       backref=db.backref('batches', lazy='dynamic'))
    
    def __repr__(self):
        return f'{self.year} year {self.batch_name} batch' 