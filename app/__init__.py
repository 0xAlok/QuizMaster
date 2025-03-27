from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # where to redirect if user is not logged in

def create_app():
    app = Flask(__name__)
    
    # Configure the SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    # Import user model for login_manager
    from app.models.user import User, Admin
    
    @login_manager.user_loader
    def load_user(user_id):
        # Check if it's an admin
        if user_id.startswith('admin_'):
            real_id = user_id.split('admin_')[1]
            return Admin.query.get(int(real_id))
        # Otherwise it's a regular user
        return User.query.get(int(user_id))
    
    return app