from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# Import generate_password_hash here
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import User, Admin
from datetime import datetime
from .forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If already logged in, redirect based on user type
        if isinstance(current_user, Admin):
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Check if it's an admin login
        if form.is_admin.data:
            admin = Admin.query.filter_by(username=form.username.data).first()
            if admin and admin.check_password(form.password.data):
                login_user(admin)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin.dashboard'))
            flash('Invalid admin credentials', 'danger')
        else:
            # Regular user login
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('user.dashboard'))
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Redirect based on user type if already logged in
        if isinstance(current_user, Admin):
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.dashboard')) # Assuming a user dashboard exists

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data)
            # Use form.dob.data directly as it's already a date object
            dob_data = form.dob.data # Assign directly

            new_user = User(
                username=form.email.data,
                full_name=form.full_name.data,
                password=hashed_password,  # Changed from password_hash
                qualification=form.qualification.data,
                dob=dob_data # Use the date object
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback() # Rollback in case of error
            flash(f'An error occurred during registration: {e}', 'danger')
            # Log the error for debugging (optional but recommended)
            # current_app.logger.error(f"Registration error: {e}")
            # current_app.logger.error(traceback.format_exc()) # More detailed traceback
            print(f"Registration error: {e}") # Print error for Render logs

    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))