import os
import sys
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Initialize extensions globally
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def create_app(config_class=Config):
    """
    Flask Application Factory.
    Registers extensions, configures settings, and hooks up blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS for cross-origin APIs
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize JWT Manager
    jwt.init_app(app)
    
    # Initialize Limiter
    limiter.init_app(app)

    # Import blueprints inside factory to avoid circular dependencies
    from app.routes.chat import chat_bp
    from app.routes.admin import admin_bp

    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    return app
