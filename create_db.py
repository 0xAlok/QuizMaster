from app import create_app, db
from app.models.user import Admin 

def init_db():
    """
    Initializes the database by creating all tables defined in the models
    and ensures a default admin user exists.
    """
    print("Initializing database...")
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created.")
        
        admin_username = 'admin@quizmaster.com'
        existing_admin = Admin.query.filter_by(username=admin_username).first()
        
        if not existing_admin:
            print(f"Creating default admin user: {admin_username}")
            try:
                default_admin = Admin(username=admin_username)
                default_admin.set_password('admin') 
                db.session.add(default_admin)
                db.session.commit()
                print('Default admin user created successfully.')
            except Exception as e:
                db.session.rollback()
                print(f"Error creating default admin user: {e}")
        else:
            print(f"Admin user '{admin_username}' already exists.")
        
        print('Database initialization process completed.')

if __name__ == '__main__':
    init_db()
