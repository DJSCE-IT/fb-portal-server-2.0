from app import db

class FeedbackInstance(db.Model):
    """Feedback instance model"""
    id = db.Column(db.Integer, primary_key=True)
    instance_name = db.Column(db.String(200), nullable=True)
    is_latest = db.Column(db.Boolean, default=False)
    is_selected = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'{self.instance_name} {self.is_selected}'
    
class MetaInfo(db.Model):
    """Meta information model"""
    id = db.Column(db.Integer, primary_key=True)
    secret_code = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'{self.id} {self.secret_code}' 