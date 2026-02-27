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
