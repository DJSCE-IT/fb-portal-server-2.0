from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from api.config.config import Config

# Initialize Flask extensions
mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    CORS(app)

    # Initialize MongoDB
    mongo.init_app(app)

    # Register blueprints
    from api.routes import auth, users, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(main.bp)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
