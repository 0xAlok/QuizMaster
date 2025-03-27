from app import create_app, db
from app.models import User, Admin, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the database and create admin user"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin already exists
        admin = Admin.query.first()
        if not admin:
            # Create an admin user
            admin = Admin(username='admin@quizmaster.com')
            admin.set_password('admin')
            db.session.add(admin) # Corrected variable name
            db.session.commit()
            print('Admin user created successfully')
        else:
            print('Admin user already exists')
        
        print('Database initialized successfully')

if __name__ == '__main__':
    init_db()