# routes.py
# Defines all main application routes via a Flask Blueprint. This module handles
# the request/response cycle for every page and action in the app, delegating all
# database operations to data.py and keeping route handlers focused purely on HTTP
# logic, validation, and template rendering.
#
# All routes are protected by @login_required — unauthenticated users are
# redirected to the login page automatically by Flask-Login.
#
#
# Dashboard:
#   - GET  /
#       Loads the current user's data and computes derived stats (balance,
#       total expenses, per-category totals, savings rate) before rendering
#       the main dashboard. Category totals are also serialized to JSON for
#       use in the frontend chart.
#
#
# Expenses:
#   - GET  /expenses
#       Renders the full expense list with running balance and total.
#
#   - POST /add
#       Validates form input (description, category, and a positive amount),
#       then inserts a new expense via data.py. On error, redirects back to
#       the referring page to preserve context (e.g. dashboard or expenses).
#
#   - POST /delete/<index>
#       Deletes the expense at the given list position. Flashes a confirmation
#       with the deleted expense's name on success, or an error if not found.
#
#   - POST /edit/<index>
#       Validates and applies updated fields to the expense at the given
#       position. Returns success or not-found feedback via flash messages.
#
#
# Settings:
#   - GET  /settings
#       Renders the settings page with the current user's salary and data.
#
#   - POST /update-salary
#       Validates and persists a new salary value. Rejects negative numbers.
#
#   - POST /reset
#       Wipes all expenses and resets salary to 0.0. Requires the user to
#       type "RESET" exactly in the confirmation field to prevent accidents.
#
#
# Export:
#   - GET  /export
#       Generates a CSV file in-memory containing all of the user's expenses
#       (description, category, amount) followed by a summary block with
#       salary, total expenses, and remaining balance. Returned as a direct
#       file download named 'budget_export.csv'.
#
#
# Dependencies:
#   - Flask-Login  : Session-aware current_user and @login_required guard.
#   - data.py      : All database reads and writes (load, save, add, delete, edit, reset).
#   - csv / io     : In-memory CSV generation for the export route.
#   - json         : Serializes category totals for the dashboard chart.

import csv
import io
import json
import calendar
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from .models import db
from datetime import date, datetime
from .data import (
    load_data, save_salary, add_expense as db_add_expense,
    delete_expense as db_delete_expense, edit_expense as db_edit_expense,
    calculate_balance, get_category_totals, get_categories,
    get_category_budgets, save_category_budget, delete_category_budget,
    reset_data
)

main = Blueprint('main', __name__)


def _selected_month() -> tuple[int, int, str]:
    """Parse ?month=YYYY-MM, falling back to the current local month."""
    raw = request.args.get('month', '').strip()
    try:
        selected = datetime.strptime(raw, '%Y-%m') if raw else datetime.now()
    except ValueError:
        selected = datetime.now()
    return selected.year, selected.month, selected.strftime('%Y-%m')


def _shift_month(year: int, month: int, offset: int) -> str:
    month_index = year * 12 + month - 1 + offset
    return f'{month_index // 12:04d}-{month_index % 12 + 1:02d}'


def _parse_expense_date(raw: str) -> date | None:
    try:
        return datetime.strptime(raw, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


# ── Dashboard ─────────────────────────────────────────────────────────────────

@main.route('/')
@login_required
def dashboard():
    year, month, month_value = _selected_month()
    data           = load_data(current_user.id, year=year, month=month)
    balance        = calculate_balance(data['salary'], data['expenses'])
    category_totals = get_category_totals(data['expenses'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    savings_rate   = round((balance / data['salary'] * 100), 1) if data['salary'] > 0 else 0
    budgets = get_category_budgets(current_user.id)
    budget_status = []
    for budget in budgets:
        spent = category_totals.get(budget['category'], 0.0)
        limit = budget['amount']
        budget_status.append({
            **budget,
            'spent': spent,
            'remaining': limit - spent,
            'percent': round((spent / limit * 100), 1) if limit > 0 else 0,
        })
    return render_template(
        'dashboard.html',
        data=data,
        balance=balance,
        total_expenses=total_expenses,
        category_totals=category_totals,
        savings_rate=savings_rate,
        category_totals_json=json.dumps(category_totals),
        current_year=year,
        selected_month=month_value,
        selected_month_label=f'{calendar.month_name[month]} {year}',
        previous_month=_shift_month(year, month, -1),
        next_month=_shift_month(year, month, 1),
        is_current_month=(year == datetime.now().year and month == datetime.now().month),
        budget_status=budget_status,
        default_expense_date=(
            date.today().isoformat()
            if year == datetime.now().year and month == datetime.now().month
            else f'{month_value}-01'
        ),
    )


# ── Expenses ──────────────────────────────────────────────────────────────────

@main.route('/expenses')
@login_required
def expenses():
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    month_value = request.args.get('month', '').strip()
    year = month = None
    if month_value:
        try:
            parsed_month = datetime.strptime(month_value, '%Y-%m')
            year, month = parsed_month.year, parsed_month.month
        except ValueError:
            month_value = ''

    data = load_data(
        current_user.id, year=year, month=month,
        search=search, category=category,
    )
    balance        = calculate_balance(data['salary'], data['expenses'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    return render_template('expenses.html', data=data, balance=balance,
                           total_expenses=total_expenses,
                           categories=get_categories(current_user.id),
                           filters={'q': search, 'category': category, 'month': month_value},
                           default_expense_date=(
                               f'{month_value}-01' if month_value
                               else date.today().isoformat()
                           ))


@main.route('/add', methods=['POST'])
@login_required
def add_expense():
    description = request.form.get('description', '').strip()
    category    = request.form.get('category', '').strip()
    amount_str  = request.form.get('amount', '').strip()
    expense_date = _parse_expense_date(request.form.get('expense_date', ''))

    if not description:
        flash('Description is required.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    if not category:
        flash('Category is required.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    if not expense_date:
        flash('Please enter a valid expense date.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('Please enter a valid positive amount.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))

    db_add_expense(current_user.id, description, category, amount, expense_date)
    flash(f'Expense "{description}" added successfully.', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@main.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    removed = db_delete_expense(current_user.id, expense_id)
    if removed:
        flash(f'"{removed["description"]}" deleted.', 'success')
    else:
        flash('Expense not found.', 'error')
    return redirect(request.referrer or url_for('main.expenses'))


@main.route('/edit/<int:expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    description = request.form.get('description', '').strip()
    category    = request.form.get('category', '').strip()
    amount_str  = request.form.get('amount', '').strip()
    expense_date = _parse_expense_date(request.form.get('expense_date', ''))

    if not description or not category or not expense_date:
        flash('Description, category, and a valid date are required.', 'error')
        return redirect(request.referrer or url_for('main.expenses'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('Please enter a valid positive amount.', 'error')
        return redirect(url_for('main.expenses'))

    success = db_edit_expense(
        current_user.id, expense_id, description, category, amount, expense_date
    )
    if success:
        flash('Expense updated successfully.', 'success')
    else:
        flash('Expense not found.', 'error')
    return redirect(request.referrer or url_for('main.expenses'))


@main.route('/api/monthly-expenses')
@login_required
def monthly_expenses_api():
    """Returns monthly expense totals for the current year as JSON."""
    from flask import jsonify
    
    try:
        year = int(request.args.get('year', datetime.now().year))
    except ValueError:
        year = datetime.now().year
    data   = load_data(current_user.id)
    salary = data['salary']
    
    # Query dated expenses directly for the requested calendar year.
    from .models import Expense
    monthly = {m: 0.0 for m in range(1, 13)}
    
    expenses = (
        Expense.query
        .filter_by(user_id=current_user.id)
        .filter(db.extract('year', Expense.expense_date) == year)
        .all()
    )
    
    for e in expenses:
        monthly[e.expense_date.month] += e.amount
    
    return jsonify({
        'salary':  salary,
        'monthly': [{'month': m, 'total': round(monthly[m], 2)} for m in range(1, 13)]
    })

# ── Settings ──────────────────────────────────────────────────────────────────

@main.route('/settings')
@login_required
def settings():
    data = load_data(current_user.id)
    return render_template(
        'settings.html',
        data=data,
        category_budgets=get_category_budgets(current_user.id),
        categories=get_categories(current_user.id),
    )


@main.route('/update-salary', methods=['POST'])
@login_required
def update_salary():
    try:
        salary = float(request.form.get('salary', 0))
        if salary < 0:
            raise ValueError
        save_salary(current_user.id, salary)
        flash('Salary updated successfully.', 'success')
    except ValueError:
        flash('Please enter a valid salary.', 'error')
    return redirect(url_for('main.settings'))


@main.route('/category-budget', methods=['POST'])
@login_required
def update_category_budget():
    category = request.form.get('category', '').strip()
    try:
        amount = float(request.form.get('amount', ''))
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('Enter a category and a positive budget amount.', 'error')
        return redirect(url_for('main.settings'))
    if not category:
        flash('Category is required.', 'error')
        return redirect(url_for('main.settings'))
    save_category_budget(current_user.id, category, amount)
    flash(f'Monthly budget for {category} saved.', 'success')
    return redirect(url_for('main.settings'))


@main.route('/category-budget/<int:budget_id>/delete', methods=['POST'])
@login_required
def remove_category_budget(budget_id):
    if delete_category_budget(current_user.id, budget_id):
        flash('Category budget removed.', 'success')
    else:
        flash('Category budget not found.', 'error')
    return redirect(url_for('main.settings'))


@main.route('/reset', methods=['POST'])
@login_required
def reset():
    confirm = request.form.get('confirm', '').strip()
    if confirm == 'RESET':
        reset_data(current_user.id)
        flash('All data has been reset.', 'success')
    else:
        flash('Type RESET exactly to confirm.', 'error')
    return redirect(url_for('main.settings'))


# ── Export ────────────────────────────────────────────────────────────────────

@main.route('/export')
@login_required
def export_csv():
    data    = load_data(current_user.id)
    total   = sum(e['amount'] for e in data['expenses'])
    balance = calculate_balance(data['salary'], data['expenses'])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Description', 'Category', 'Amount'])
    for e in data['expenses']:
        writer.writerow([e['expense_date'], e['description'], e.get('category', 'Uncategorized'),
                         f"{e['amount']:.2f}"])
    writer.writerow([])
    writer.writerow(['--- SUMMARY ---', '', ''])
    writer.writerow(['Monthly Salary',    '', f"{data['salary']:.2f}"])
    writer.writerow(['Total Expenses',    '', f"{total:.2f}"])
    writer.writerow(['Remaining Balance', '', f"{balance:.2f}"])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='budget_export.csv'
    )

# ── Contact ───────────────────────────────────────────────────────────────────

@main.route('/contact')
@login_required
def contact():
    return render_template('contact.html')


@main.route('/contact/send', methods=['POST'])
@login_required
def send_contact():
    from flask_mail import Message as MailMessage
    from . import mail

    name     = request.form.get('name',     '').strip()
    email    = request.form.get('email',    '').strip()
    category = request.form.get('category', '').strip()
    message  = request.form.get('message',  '').strip()

    if not name or not email or not category or not message:
        flash('All fields are required.', 'error')
        return redirect(url_for('main.contact'))

    try:
        msg = MailMessage(
            subject  = f'[Budget Tracker] {category} from {name}',
            sender   = current_app.config['MAIL_USERNAME'],
            recipients = [current_app.config['MAIL_RECEIVER']],
            body = f"""
Name:     {name}
Email:    {email}
Category: {category}

Message:
{message}
            """.strip()
        )
        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('main.contact'))
