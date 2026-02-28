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
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from .data import (
    load_data, save_salary, add_expense as db_add_expense,
    delete_expense_by_index, edit_expense_by_index,
    calculate_balance, get_category_totals, reset_data
)

main = Blueprint('main', __name__)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@main.route('/')
@login_required
def dashboard():
    data           = load_data(current_user.id)
    balance        = calculate_balance(data['salary'], data['expenses'])
    category_totals = get_category_totals(data['expenses'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    savings_rate   = round((balance / data['salary'] * 100), 1) if data['salary'] > 0 else 0
    return render_template(
        'dashboard.html',
        data=data,
        balance=balance,
        total_expenses=total_expenses,
        category_totals=category_totals,
        savings_rate=savings_rate,
        category_totals_json=json.dumps(category_totals)
    )


# ── Expenses ──────────────────────────────────────────────────────────────────

@main.route('/expenses')
@login_required
def expenses():
    data           = load_data(current_user.id)
    balance        = calculate_balance(data['salary'], data['expenses'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    return render_template('expenses.html', data=data, balance=balance,
                           total_expenses=total_expenses)


@main.route('/add', methods=['POST'])
@login_required
def add_expense():
    description = request.form.get('description', '').strip()
    category    = request.form.get('category', '').strip()
    amount_str  = request.form.get('amount', '').strip()

    if not description:
        flash('Description is required.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))
    if not category:
        flash('Category is required.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('Please enter a valid positive amount.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))

    db_add_expense(current_user.id, description, category, amount)
    flash(f'Expense "{description}" added successfully.', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@main.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete_expense(index):
    removed = delete_expense_by_index(current_user.id, index)
    if removed:
        flash(f'"{removed["description"]}" deleted.', 'success')
    else:
        flash('Expense not found.', 'error')
    return redirect(request.referrer or url_for('main.expenses'))


@main.route('/edit/<int:index>', methods=['POST'])
@login_required
def edit_expense(index):
    description = request.form.get('description', '').strip()
    category    = request.form.get('category', '').strip()
    amount_str  = request.form.get('amount', '').strip()

    if not description or not category:
        flash('Description and category are required.', 'error')
        return redirect(url_for('main.expenses'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash('Please enter a valid positive amount.', 'error')
        return redirect(url_for('main.expenses'))

    success = edit_expense_by_index(current_user.id, index, description, category, amount)
    if success:
        flash('Expense updated successfully.', 'success')
    else:
        flash('Expense not found.', 'error')
    return redirect(url_for('main.expenses'))


# ── Settings ──────────────────────────────────────────────────────────────────

@main.route('/settings')
@login_required
def settings():
    data = load_data(current_user.id)
    return render_template('settings.html', data=data)


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
    writer.writerow(['Description', 'Category', 'Amount'])
    for e in data['expenses']:
        writer.writerow([e['description'], e.get('category', 'Uncategorized'),
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