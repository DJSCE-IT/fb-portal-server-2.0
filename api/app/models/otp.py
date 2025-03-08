from app import db
from datetime import datetime

class Otp(db.Model):
    """OTP model for user authentication"""
    id = db.Column(db.Integer, primary_key=True)
    Otp = db.Column(db.String(100), nullable=False)
    timeOfGeneration = db.Column(db.DateTime, default=datetime.utcnow)
    LoginUser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    LoginUser = db.relationship('User', backref='otps')
    
    def __repr__(self):
        return f'{self.id}-> id || {self.LoginUser.email}->Student || {self.Otp}=> OTP' 