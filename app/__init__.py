from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  
login_manager.login_message_category = 'info' 

def create_app(config_object=None):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_object: Optional configuration object to use.
    
    Returns:
        The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True) 

    # --- Configuration ---
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24), 
        SQLALCHEMY_DATABASE_URI='sqlite:///quiz_master.db', 
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config_object:
        app.config.from_object(config_object)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass 

    # --- Initialize Extensions ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # --- Register Blueprints ---
    from app.controllers.auth import auth_bp
    from app.controllers.admin import admin_bp
    from app.controllers.user import user_bp
    from app.controllers.api import api_bp 
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp) 
    
    # --- User Loader for Flask-Login ---
    from app.models.user import User, Admin
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        Flask-Login user loader callback.
        Loads a User or Admin based on the stored user ID, which includes
        a prefix for Admins ('admin_').
        """
        if user_id is not None and user_id.startswith('admin_'):
            try:
                admin_id = int(user_id.split('admin_')[1])
                return Admin.query.get(admin_id)
            except (IndexError, ValueError):
                return None
        elif user_id is not None:
            try:
                return User.query.get(int(user_id))
            except ValueError:
                return None
        return None 

    return app
