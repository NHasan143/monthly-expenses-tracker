# auth.py
# Handles all authentication-related routes for the application using a Flask Blueprint.
#
# This module defines five routes:
#
#   - /register          : Accepts GET and POST requests. On GET, renders the registration form.
#                          On POST, validates user input (required fields, minimum lengths,
#                          password confirmation, and uniqueness of username/email), hashes the
#                          password with bcrypt, persists the new User to the database, logs
#                          them in immediately, sends a welcome email, and redirects to dashboard.
#
#   - /login             : Accepts GET and POST requests. On GET, renders the login form.
#                          On POST, validates credentials against the database using bcrypt,
#                          supports a "remember me" option, and redirects to either the originally
#                          requested page (via the `next` query parameter) or the dashboard.
#
#   - /logout            : GET only, protected by @login_required. Logs the current user out
#                          and redirects to the login page.
#
#   - /forgot-password   : Accepts GET and POST requests. On GET, renders the email input form.
#                          On POST, looks up the account, generates a signed reset token, and
#                          emails the reset link. Always shows the same generic confirmation
#                          message regardless of whether the email exists — this prevents
#                          user-enumeration attacks.
#
#   - /reset-password/<token> : Accepts GET and POST requests. On GET, validates the token and
#                               renders the new-password form. On POST, validates the token again,
#                               updates the password hash, and redirects to login. The token is
#                               verified on both GET and POST to guard against replay attacks.
#
# Dependencies:
#   - Flask-Login    : Manages user session state (login_user, logout_user, current_user).
#   - Flask-Bcrypt   : Handles secure password hashing and verification.
#   - SQLAlchemy     : Persists and queries User records via the shared `db` instance.
#   - email_utils.py : Provides send_welcome_email, send_password_reset_email,
#                      generate_reset_token, and verify_reset_token.
#
# All routes redirect authenticated users away from the register/login/forgot/reset pages
# to prevent redundant access. Flash messages are used throughout to surface validation
# errors and success confirmations to the user.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User
from . import bcrypt
from .email_utils import (
    send_welcome_email,
    send_password_reset_email,
    generate_reset_token,
    verify_reset_token,
)

auth = Blueprint('auth', __name__)


# ── Register ──────────────────────────────────────────────────────────────────

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Already logged in — send to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # ── Validation ────────────────────────────────────────────
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'error')
            return render_template('register.html')

        # ── Create user ───────────────────────────────────────────
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        send_welcome_email(user)
        flash(f'Welcome, {username}! Your account has been created.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


# ── Login ─────────────────────────────────────────────────────────────────────

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in — send to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash('Incorrect email or password.', 'error')
            return render_template('login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.username}!', 'success')

        # Redirect to the page they were trying to visit, or dashboard
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('login.html')


# ── Logout ────────────────────────────────────────────────────────────────────

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


# ── Forgot Password ───────────────────────────────────────────────────────────  ← NEW ROUTE

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # Already logged in — no need to reset password
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot_password.html')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with that email address.', 'error')
            return render_template('forgot_password.html')

        token     = generate_reset_token(user.email)
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        send_password_reset_email(user, reset_url)

        flash(
            'A reset link has been sent to your inbox. '
            'Check your spam folder if you don\'t see it.',
            'success'
        )
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


# ── Reset Password ────────────────────────────────────────────────────────────  ← NEW ROUTE

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Already logged in — no need to reset password
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # Validate the token on GET and POST both — guards against replay attacks
    email = verify_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Account not found. Please register.', 'error')
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # ── Validation ────────────────────────────────────────────
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('reset_password.html', token=token)

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)

        # ── Update password ───────────────────────────────────────
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()

        flash('Your password has been updated. Please sign in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)