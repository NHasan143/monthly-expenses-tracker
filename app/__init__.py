# __init__.py
# Application factory for the Flask app. Centralizing app creation in
# create_app() allows the application to be instantiated with different
# configurations (e.g. testing vs. production) and avoids circular imports
# by deferring extension and blueprint registration until call time.
#
#
# Module-level Instances:
#   - bcrypt
#       A Bcrypt instance created here so it can be imported directly by
#       auth.py for password hashing and verification without going through
#       the app object. Bound to the app via bcrypt.init_app(app) inside
#       create_app().
#
#   - mail
#       A Mail instance created here so it can be imported directly by
#       email_utils.py for sending transactional emails (welcome + password
#       reset). Bound to the app via mail.init_app(app) inside create_app().
#
#
# Internal Helper:
#   - _get_database_url()
#       Resolves the database connection string at startup. On Render (and
#       similar PaaS platforms), DATABASE_URL is injected automatically as
#       an environment variable using the legacy 'postgres://' scheme.
#       SQLAlchemy 1.4+ requires 'postgresql://', so the prefix is corrected
#       here if needed. Falls back to a local SQLite file (users.db) when
#       DATABASE_URL is not set, keeping the development setup dependency-free.
#
#
# create_app():
#   The application factory. Builds and returns a fully configured Flask app.
#   Initialization is performed in four stages:
#
#   1. Config
#       Sets the secret key (used for session signing and CSRF protection),
#       the database URI from _get_database_url(), and SQLAlchemy options:
#         - pool_pre_ping  : Tests connections before use to handle dropped
#                            or timed-out database connections gracefully.
#         - pool_recycle   : Recycles connections every 5 minutes to prevent
#                            stale connection errors on long-running deployments.
#       Also reads mail configuration from environment variables:
#         MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL,
#         MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
#
#   2. Extensions
#       Initializes SQLAlchemy (db), Bcrypt, Flask-Mail, and Flask-Login
#       against the app. Flask-Login is configured to redirect unauthenticated
#       users to the auth.login route, flashing an error-category message. The
#       user_loader callback is registered here to tell Flask-Login how to
#       reload a user from their session-stored ID on each request.
#
#   3. Database Tables
#       Calls db.create_all() inside an app context to create any tables that
#       do not already exist. This is a no-op on subsequent startups and is
#       safe for both SQLite (development) and PostgreSQL (production).
#
#   4. Blueprints
#       Registers the auth and main blueprints, which define all URL routes
#       for authentication (auth.py) and the main application (routes.py).

import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

bcrypt = Bcrypt()
mail   = Mail()


def _get_database_url() -> str:
    """
    Read DATABASE_URL from the environment (set automatically by Render).
    Render provides a 'postgres://' URL but SQLAlchemy 1.4+ requires
    'postgresql://' — fix it here if needed.
    Falls back to local SQLite for development.
    """
    url = os.environ.get('DATABASE_URL')
    if url:
        # Fix Render's legacy postgres:// scheme
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    # Local development fallback
    return 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.db')


def create_app():
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI']        = _get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS']      = {
        'pool_pre_ping': True,   # reconnect if connection dropped
        'pool_recycle':  300,    # recycle connections every 5 minutes
    }

    # ── Mail Config ───────────────────────────────────────────────  ← NEW BLOCK
    # All values are read from environment variables (your .env file locally,
    # or the Render dashboard in production). Nothing is hardcoded here.
    # Example for Gmail:
    #   MAIL_SERVER=smtp.gmail.com
    #   MAIL_PORT=587
    #   MAIL_USE_TLS=true
    #   MAIL_USERNAME=you@gmail.com
    #   MAIL_PASSWORD=your-16-char-app-password
    #   MAIL_DEFAULT_SENDER=you@gmail.com
    app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT']           = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS']        = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL']        = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get(
        'MAIL_DEFAULT_SENDER',
        os.environ.get('MAIL_USERNAME', 'noreply@budgettracker.app')
    )

    # ── Extensions ────────────────────────────────────────────────
    from .models import db, User
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view        = 'auth.login'
    login_manager.login_message     = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Create DB tables ──────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Blueprints ────────────────────────────────────────────────
    from .auth import auth
    from .routes import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app