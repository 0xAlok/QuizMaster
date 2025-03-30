from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash 
from app import db
from app.models.user import User, Admin
from .forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Serves the main landing page."""
    # Redirect logged-in users to their respective dashboards
    if current_user.is_authenticated:
        dashboard_endpoint = 'admin.dashboard' if isinstance(current_user, Admin) else 'user.dashboard'
        return redirect(url_for(dashboard_endpoint))
    # Otherwise, show the landing page
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user and admin login."""
    if current_user.is_authenticated:
        dashboard_endpoint = 'admin.dashboard' if isinstance(current_user, Admin) else 'user.dashboard'
        return redirect(url_for(dashboard_endpoint))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        is_admin_login = form.is_admin.data

        if is_admin_login:
            model = Admin
            success_redirect_endpoint = 'admin.dashboard'
            error_message = 'Invalid admin credentials'
        else:
            model = User
            success_redirect_endpoint = 'user.dashboard'
            error_message = 'Invalid username or password' 

        entity = model.query.filter_by(username=username).first()

        if entity and entity.check_password(password):
            login_user(entity)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for(success_redirect_endpoint))
        else:
            flash(error_message, 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if current_user.is_authenticated:
        dashboard_endpoint = 'admin.dashboard' if isinstance(current_user, Admin) else 'user.dashboard'
        return redirect(url_for(dashboard_endpoint)) 

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(username=form.email.data).first()
            if existing_user:
                flash('Username (email) already exists. Please choose a different one or login.', 'warning')
            else:
                hashed_password = generate_password_hash(form.password.data)
                new_user = User(
                    username=form.email.data,
                    full_name=form.full_name.data,
                    password=hashed_password,
                    qualification=form.qualification.data,
                    dob=form.dob.data 
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback() 
            flash(f'An error occurred during registration: {e}', 'danger')
            print(f"Registration error: {e}") 

    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info') 
    return redirect(url_for('auth.login'))
