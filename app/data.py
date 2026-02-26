import os
import json

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'budget_data.json')


def load_data() -> dict:
    """Load budget data from JSON file. Returns default structure if file is missing or corrupt."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                raw = json.load(f)
                return {
                    "salary": float(raw.get("salary", 0.0)),
                    "expenses": raw.get("expenses", [])
                }
        except (json.JSONDecodeError, ValueError):
            pass
    return {"salary": 0.0, "expenses": []}


def save_data(data: dict) -> None:
    """Persist budget data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def calculate_balance(salary: float, expenses: list) -> float:
    """Return remaining balance after all expenses."""
    return salary - sum(e['amount'] for e in expenses)


def get_category_totals(expenses: list) -> dict:
    """Aggregate expense amounts by category."""
    totals = {}
    for e in expenses:
        cat = e.get('category', 'Uncategorized')
        totals[cat] = totals.get(cat, 0.0) + e['amount']
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def reset_data() -> dict:
    """Delete the data file and return a fresh default structure."""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return {"salary": 0.0, "expenses": []}
