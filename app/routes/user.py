from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.subject import Subject
from app.models.score import Score

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Decorator to ensure only regular users (not admins) access user routes
def user_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, User):
            flash('This page is for regular users only', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@user_required
def dashboard():
    # Get available subjects for the user
    subjects = Subject.query.all()
    # Get user's past quiz attempts
    scores = Score.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/dashboard.html', 
                           subjects=subjects,
                           scores=scores)