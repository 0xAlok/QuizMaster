from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import Admin, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to check if user is an admin
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            flash('You must be an admin to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Count of entities for dashboard overview
    user_count = User.query.count()
    # We'll add more counts later as other models are used
    
    return render_template('admin/dashboard.html', 
                           user_count=user_count)

@admin_bp.route('/users')
@admin_required
def users():
    users_list = User.query.all()
    return render_template('admin/users.html', users=users_list)