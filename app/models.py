# models.py
# Defines the SQLAlchemy ORM models and the shared `db` instance used throughout
# the application. This module is the single source of truth for the database
# schema — any changes to the structure of the tables should be made here.
#
#
# Shared Instance:
#   - db
#       A SQLAlchemy instance initialized here and registered to the Flask app
#       via db.init_app(app) in the application factory. Imported and used
#       across models.py, data.py, and anywhere else database access is needed.
#
#
# Models:
#
#   User  (table: users)
#       Represents a registered account. Inherits from UserMixin to integrate
#       with Flask-Login, which uses this model to manage session state.
#       Fields    : id, username (unique), email (unique), password_hash
#       Relations : One-to-one with UserSettings, one-to-many with Expense.
#                   Both relationships cascade deletes, so removing a User also
#                   removes all their associated settings and expenses.
#
#   UserSettings  (table: user_settings)
#       Stores per-user configuration — currently limited to monthly salary.
#       Linked to User via a unique foreign key, enforcing a strict one-to-one
#       relationship. Created automatically by data.py if it does not yet exist.
#       Fields    : id, user_id (FK → users.id), salary (default: 0.0)
#
#   Expense  (table: expenses)
#       Represents a single expense entry belonging to a user. Ordered by
#       created_at throughout the application to maintain a consistent index-
#       based ordering relied upon by data.py for edit and delete operations.
#       Fields    : id, user_id (FK → users.id), description, category
#                   (default: 'Uncategorized'), amount, created_at (auto-set)
#       Methods:
#         - to_dict() : Returns a plain { id, description, category, amount }
#                       dict so that routes and templates remain decoupled from
#                       the ORM model and require no changes after migration.
#
#
# Dependencies:
#   - Flask-SQLAlchemy : ORM layer and `db` instance.
#   - Flask-Login      : UserMixin base class for session management on User.
#   - datetime         : Supplies the default UTC timestamp for Expense.created_at.

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Represents a registered user."""

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationships
    settings = db.relationship('UserSettings', backref='user', uselist=False,
                                cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user',
                                cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class UserSettings(db.Model):
    """Stores per-user settings — currently just monthly salary."""

    __tablename__ = 'user_settings'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    salary  = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f'<UserSettings user_id={self.user_id} salary={self.salary}>'


class Expense(db.Model):
    """Represents a single expense entry belonging to a user."""

    __tablename__ = 'expenses'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category    = db.Column(db.String(100), nullable=False, default='Uncategorized')
    amount      = db.Column(db.Float, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Return a plain dict so routes/templates stay unchanged."""
        return {
            'id':          self.id,
            'description': self.description,
            'category':    self.category,
            'amount':      self.amount,
        }

    def __repr__(self):
        return f'<Expense {self.description} ${self.amount}>'

