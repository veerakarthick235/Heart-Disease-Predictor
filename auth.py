"""
auth.py — Authentication Blueprint
Handles: register, login, logout, profile routes.
"""

import re
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, session
)
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import limiter

auth = Blueprint('auth', __name__)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _validate_password(password):
    """Minimum: 8 chars, 1 uppercase, 1 digit."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number.'
    return True, None


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('predict_page'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        errors = []

        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if not _validate_email(email):
            errors.append('Please enter a valid email address.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        valid_pwd, pwd_msg = _validate_password(password)
        if not valid_pwd:
            errors.append(pwd_msg)

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('register.html',
                                   full_name=full_name, email=email)

        # Attempt user creation
        user, error = User.create(full_name, email, password)
        if error:
            flash(error, 'error')
            return render_template('register.html',
                                   full_name=full_name, email=email)

        login_user(user, remember=True)
        flash(f'Welcome, {user.full_name}! Your account has been created.', 'success')
        return redirect(url_for('predict_page'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('predict_page'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember_me') == 'on'

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html', email=email)

        user = User.get_by_email(email)

        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html', email=email)

        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return render_template('login.html', email=email)

        login_user(user, remember=remember)
        user.update_last_login()

        flash(f'Welcome back, {user.full_name}!', 'success')
        
        # Redirect to the originally requested page if applicable
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('predict_page'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    name = current_user.full_name
    logout_user()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/profile')
@login_required
def profile():
    """User profile page with stats."""
    stats = current_user.get_prediction_stats()
    return render_template('profile.html', stats=stats)
