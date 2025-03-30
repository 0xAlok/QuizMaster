from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """Represents a user who can take quizzes."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)  
    password = db.Column(db.String(100), nullable=False) 
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    scores = db.relationship('Score', backref='user', lazy=True, cascade="all, delete-orphan") 
    
    def set_password(self, password):
        """Hashes the provided password and stores it."""
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        """Provides a developer-friendly representation of the User object."""
        return f'<User {self.username}>'

class Admin(db.Model, UserMixin):
    """Represents an administrator user with management privileges."""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 
    
    def set_password(self, password):
        """Hashes the provided password and stores it."""
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)
        
    def get_id(self):
        """
        Overrides the default get_id for Flask-Login.
        Prefixes the ID with 'admin_' to prevent collisions with User IDs
        in the user loader callback.
        """
        return f"admin_{self.id}"
    
    def __repr__(self):
        """Provides a representation of the Admin object."""
        return f'<Admin {self.username}>'
