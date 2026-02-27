import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


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

    # ── Extensions ────────────────────────────────────────────────
    from .models import db, User
    db.init_app(app)
    bcrypt.init_app(app)

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
