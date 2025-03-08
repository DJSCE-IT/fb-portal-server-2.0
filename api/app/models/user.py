from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model equivalent to Django's User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_superuser = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class MyUser(db.Model):
    """Extension of the User model with additional fields"""
    email = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('myuser', uselist=False))
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
    
    def __repr__(self):
        return f'<MyUser {self.name} ({self.email})>' 