import csv
import io
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from .data import load_data, save_data, calculate_balance, get_category_totals, reset_data

main = Blueprint('main', __name__)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@main.route('/')
def dashboard():
    data = load_data()
    balance = calculate_balance(data['salary'], data['expenses'])
    category_totals = get_category_totals(data['expenses'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    savings_rate = round((balance / data['salary'] * 100), 1) if data['salary'] > 0 else 0
    return render_template(
        'dashboard.html',
        data=data,
        balance=balance,
        total_expenses=total_expenses,
        category_totals=category_totals,
        savings_rate=savings_rate,
        category_totals_json=json.dumps(category_totals)
    )


# ── Expenses ───────────────────────────────────────────────────────────────────

@main.route('/expenses')
def expenses():
    data = load_data()
    balance = calculate_balance(data['salary'], data['expenses'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    return render_template('expenses.html', data=data, balance=balance, total_expenses=total_expenses)


@main.route('/add', methods=['POST'])
def add_expense():
    data = load_data()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    amount_str = request.form.get('amount', '').strip()

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

    data['expenses'].append({
        'description': description,
        'category': category,
        'amount': amount
    })
    save_data(data)
    flash(f'Expense "{description}" added successfully.', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@main.route('/delete/<int:index>', methods=['POST'])
def delete_expense(index):
    data = load_data()
    if 0 <= index < len(data['expenses']):
        removed = data['expenses'].pop(index)
        save_data(data)
        flash(f'"{removed["description"]}" deleted.', 'success')
    else:
        flash('Expense not found.', 'error')
    return redirect(request.referrer or url_for('main.expenses'))


@main.route('/edit/<int:index>', methods=['POST'])
def edit_expense(index):
    data = load_data()
    if not (0 <= index < len(data['expenses'])):
        flash('Expense not found.', 'error')
        return redirect(url_for('main.expenses'))

    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    amount_str = request.form.get('amount', '').strip()

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

    data['expenses'][index] = {
        'description': description,
        'category': category,
        'amount': amount
    }
    save_data(data)
    flash('Expense updated successfully.', 'success')
    return redirect(url_for('main.expenses'))


# ── Settings ──────────────────────────────────────────────────────────────────

@main.route('/settings')
def settings():
    data = load_data()
    return render_template('settings.html', data=data)


@main.route('/update-salary', methods=['POST'])
def update_salary():
    data = load_data()
    try:
        salary = float(request.form.get('salary', 0))
        if salary < 0:
            raise ValueError
        data['salary'] = salary
        save_data(data)
        flash('Salary updated successfully.', 'success')
    except ValueError:
        flash('Please enter a valid salary.', 'error')
    return redirect(url_for('main.settings'))


@main.route('/reset', methods=['POST'])
def reset():
    confirm = request.form.get('confirm', '').strip()
    if confirm == 'RESET':
        reset_data()
        flash('All data has been reset.', 'success')
    else:
        flash('Type RESET exactly to confirm.', 'error')
    return redirect(url_for('main.settings'))


# ── Export ────────────────────────────────────────────────────────────────────

@main.route('/export')
def export_csv():
    data = load_data()
    total = sum(e['amount'] for e in data['expenses'])
    balance = calculate_balance(data['salary'], data['expenses'])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Description', 'Category', 'Amount'])
    for e in data['expenses']:
        writer.writerow([e['description'], e.get('category', 'Uncategorized'), f"{e['amount']:.2f}"])
    writer.writerow([])
    writer.writerow(['--- SUMMARY ---', '', ''])
    writer.writerow(['Monthly Salary', '', f"{data['salary']:.2f}"])
    writer.writerow(['Total Expenses', '', f"{total:.2f}"])
    writer.writerow(['Remaining Balance', '', f"{balance:.2f}"])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='budget_export.csv'
    )
