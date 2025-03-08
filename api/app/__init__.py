from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60 * 60 * 6  # 6 hours
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 60 * 60 * 24  # 24 hours
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('MONGODB_URI', 'sqlite:///feedback_portal.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('EMAIL_HOST')
    app.config['MAIL_PORT'] = int(os.environ.get('EMAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_HOST_USER')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_HOST_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_HOST_USER')
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.feedback import feedback_bp
    from app.routes.subject import subject_bp
    from app.routes.batch import batch_bp
    from app.routes.user import user_bp
    from app.routes.instance import instance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(feedback_bp, url_prefix='/api')
    app.register_blueprint(subject_bp, url_prefix='/api')
    app.register_blueprint(batch_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(instance_bp, url_prefix='/api')
    
    # Create a route for the root path
    @app.route('/')
    def welcome():
        return 'Welcome to the Feedback Portal API'
    
    return app 