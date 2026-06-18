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

from datetime import date
from sqlalchemy import extract, or_
from .models import db, CategoryBudget, Expense, UserSettings


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

def load_data(user_id: int, year: int | None = None, month: int | None = None,
              search: str = '', category: str = '') -> dict:
    """
    Return a dict with 'salary' and 'expenses' list for a user.
    Each expense is a plain dict: {id, description, category, amount}.
    """
    settings = _get_or_create_settings(user_id)
    query = Expense.query.filter_by(user_id=user_id)
    if year:
        query = query.filter(extract('year', Expense.expense_date) == year)
    if month:
        query = query.filter(extract('month', Expense.expense_date) == month)
    if search:
        term = f'%{search}%'
        query = query.filter(or_(
            Expense.description.ilike(term),
            Expense.category.ilike(term),
        ))
    if category:
        query = query.filter(Expense.category == category)
    expenses = query.order_by(Expense.expense_date.asc(), Expense.id.asc()).all()
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
            amount=float(e['amount']),
            expense_date=date.fromisoformat(e.get('expense_date', date.today().isoformat()))
        ))

    db.session.commit()


def save_salary(user_id: int, salary: float) -> None:
    """Update only the salary — more efficient than save_data for settings page."""
    settings = _get_or_create_settings(user_id)
    settings.salary = float(salary)
    db.session.commit()


def add_expense(user_id: int, description: str, category: str, amount: float,
                expense_date: date) -> Expense:
    """Insert a single new expense row and return it."""
    expense = Expense(
        user_id=user_id,
        description=description,
        category=category,
        amount=float(amount),
        expense_date=expense_date,
    )
    db.session.add(expense)
    db.session.commit()
    return expense


def delete_expense(user_id: int, expense_id: int) -> dict | None:
    """Delete one expense by its stable database ID."""
    target = Expense.query.filter_by(user_id=user_id, id=expense_id).first()
    if not target:
        return None
    removed = target.to_dict()
    db.session.delete(target)
    db.session.commit()
    return removed


def edit_expense(user_id: int, expense_id: int, description: str, category: str,
                 amount: float, expense_date: date) -> bool:
    """Update one expense by its stable database ID."""
    target = Expense.query.filter_by(user_id=user_id, id=expense_id).first()
    if not target:
        return False
    target.description = description
    target.category    = category
    target.amount      = float(amount)
    target.expense_date = expense_date
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


def get_categories(user_id: int) -> list[str]:
    """Return all expense and budget categories used by a user."""
    expense_categories = {
        row[0] for row in
        db.session.query(Expense.category).filter_by(user_id=user_id).distinct().all()
    }
    budget_categories = {
        row[0] for row in
        db.session.query(CategoryBudget.category).filter_by(user_id=user_id).distinct().all()
    }
    return sorted(expense_categories | budget_categories, key=str.lower)


def get_available_months(user_id: int) -> list[str]:
    """Return populated months as YYYY-MM strings, newest first."""
    dates = (
        db.session.query(Expense.expense_date)
        .filter_by(user_id=user_id)
        .filter(Expense.expense_date.isnot(None))
        .all()
    )
    return sorted({value.strftime('%Y-%m') for (value,) in dates}, reverse=True)


def get_category_budgets(user_id: int) -> list[dict]:
    budgets = (
        CategoryBudget.query.filter_by(user_id=user_id)
        .order_by(CategoryBudget.category.asc())
        .all()
    )
    return [budget.to_dict() for budget in budgets]


def save_category_budget(user_id: int, category: str, amount: float) -> None:
    budget = CategoryBudget.query.filter_by(
        user_id=user_id, category=category
    ).first()
    if budget:
        budget.amount = float(amount)
    else:
        db.session.add(CategoryBudget(
            user_id=user_id, category=category, amount=float(amount)
        ))
    db.session.commit()


def delete_category_budget(user_id: int, budget_id: int) -> bool:
    budget = CategoryBudget.query.filter_by(user_id=user_id, id=budget_id).first()
    if not budget:
        return False
    db.session.delete(budget)
    db.session.commit()
    return True


def reset_data(user_id: int) -> dict:
    """Delete all expenses and reset salary to 0 for a user."""
    Expense.query.filter_by(user_id=user_id).delete()
    CategoryBudget.query.filter_by(user_id=user_id).delete()
    settings = _get_or_create_settings(user_id)
    settings.salary = 0.0
    db.session.commit()
    return {'salary': 0.0, 'expenses': []}
