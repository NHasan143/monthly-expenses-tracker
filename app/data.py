# data.py
# Provides all budget data operations for the application, backed by PostgreSQL
# via SQLAlchemy. This module acts as the data access layer between routes.py
# and the database models, keeping all query logic centralized and out of the
# route handlers.
#
# Public function signatures are intentionally identical to the previous JSON-
# based implementation, meaning routes.py requires no changes after the migration.
#
#
# Internal Helpers:
#   - _get_or_create_settings(user_id)
#       Fetches the UserSettings row for a given user, or creates one with a
#       default salary of 0.0 if none exists. Used internally by most functions
#       to guarantee a settings record is always present.
#
#
# Public API:
#   - load_data(user_id)
#       Returns a dict containing the user's salary and a list of all their
#       expenses ordered by creation date (ascending). Each expense is a plain
#       dict: { id, description, category, amount }.
#
#   - save_data(user_id, data)
#       Persists the user's salary and fully replaces their expense set in one
#       operation (delete-all + re-insert). Primarily used by edit operations.
#       For single add/delete actions, prefer the targeted functions below.
#
#   - save_salary(user_id, salary)
#       Updates only the user's salary without touching expenses. More efficient
#       than save_data() when only the settings page is updated.
#
#   - add_expense(user_id, description, category, amount)
#       Inserts a single new Expense row and returns the created object.
#
#   - delete_expense_by_index(user_id, index)
#       Deletes the expense at the given position in the user's ordered list.
#       Returns the deleted expense as a dict, or None if the index is out of range.
#
#   - edit_expense_by_index(user_id, index, description, category, amount)
#       Updates the fields of the expense at the given position. Returns True on
#       success, or False if the index is out of range.
#
#   - calculate_balance(salary, expenses)
#       Pure utility function. Returns the remaining balance after summing all
#       expense amounts from the provided list.
#
#   - get_category_totals(expenses)
#       Aggregates expense amounts by category from the provided list and returns
#       a dict sorted by total in descending order.
#
#   - reset_data(user_id)
#       Deletes all expenses for a user and resets their salary to 0.0.
#       Returns a clean empty data dict: { salary: 0.0, expenses: [] }.
#
#
# Dependencies:
#   - SQLAlchemy  : All database reads and writes via the shared `db` instance.
#   - models.py   : Expense and UserSettings ORM models.

from .models import db, Expense, UserSettings


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_or_create_settings(user_id: int) -> UserSettings:
    """Return the UserSettings row for a user, creating it if it doesn't exist."""
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id, salary=0.0)
        db.session.add(settings)
        db.session.commit()
    return settings


# ── Public API (same signatures as old JSON version) ─────────────────────────

def load_data(user_id: int) -> dict:
    """
    Return a dict with 'salary' and 'expenses' list for a user.
    Each expense is a plain dict: {id, description, category, amount}.
    """
    settings = _get_or_create_settings(user_id)
    expenses = (
        Expense.query
        .filter_by(user_id=user_id)
        .order_by(Expense.created_at.asc())
        .all()
    )
    return {
        'salary':   settings.salary,
        'expenses': [e.to_dict() for e in expenses]
    }


def save_data(user_id: int, data: dict) -> None:
    """
    Persist salary and the full expenses list for a user.

    This replaces the entire expense set with whatever is in data['expenses'].
    Used by edit and bulk operations. For add/delete, use the targeted
    functions below which are more efficient.
    """
    # Update salary
    settings = _get_or_create_settings(user_id)
    settings.salary = float(data.get('salary', 0.0))

    # Replace expenses: delete all then re-insert
    # (only triggered by edit_expense in routes.py — a single row update)
    Expense.query.filter_by(user_id=user_id).delete()
    for e in data.get('expenses', []):
        db.session.add(Expense(
            user_id=user_id,
            description=e['description'],
            category=e.get('category', 'Uncategorized'),
            amount=float(e['amount'])
        ))

    db.session.commit()


def save_salary(user_id: int, salary: float) -> None:
    """Update only the salary — more efficient than save_data for settings page."""
    settings = _get_or_create_settings(user_id)
    settings.salary = float(salary)
    db.session.commit()


def add_expense(user_id: int, description: str, category: str, amount: float) -> Expense:
    """Insert a single new expense row and return it."""
    expense = Expense(
        user_id=user_id,
        description=description,
        category=category,
        amount=float(amount)
    )
    db.session.add(expense)
    db.session.commit()
    return expense


def delete_expense_by_index(user_id: int, index: int) -> dict | None:
    """
    Delete the expense at position `index` in the user's ordered list.
    Returns the deleted expense dict, or None if index is out of range.
    """
    expenses = (
        Expense.query
        .filter_by(user_id=user_id)
        .order_by(Expense.created_at.asc())
        .all()
    )
    if not (0 <= index < len(expenses)):
        return None
    target = expenses[index]
    removed = target.to_dict()
    db.session.delete(target)
    db.session.commit()
    return removed


def edit_expense_by_index(user_id: int, index: int,
                           description: str, category: str, amount: float) -> bool:
    """
    Update the expense at position `index`. Returns True on success, False if
    index is out of range.
    """
    expenses = (
        Expense.query
        .filter_by(user_id=user_id)
        .order_by(Expense.created_at.asc())
        .all()
    )
    if not (0 <= index < len(expenses)):
        return False
    target = expenses[index]
    target.description = description
    target.category    = category
    target.amount      = float(amount)
    db.session.commit()
    return True


def calculate_balance(salary: float, expenses: list) -> float:
    """Return remaining balance after all expenses."""
    return salary - sum(e['amount'] for e in expenses)


def get_category_totals(expenses: list) -> dict:
    """Aggregate expense amounts by category, sorted descending."""
    totals = {}
    for e in expenses:
        cat = e.get('category', 'Uncategorized')
        totals[cat] = totals.get(cat, 0.0) + e['amount']
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def reset_data(user_id: int) -> dict:
    """Delete all expenses and reset salary to 0 for a user."""
    Expense.query.filter_by(user_id=user_id).delete()
    settings = _get_or_create_settings(user_id)
    settings.salary = 0.0
    db.session.commit()
    return {'salary': 0.0, 'expenses': []}
