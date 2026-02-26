<h1 align="center"> 💰 Monthly Expenses Tracker (Flask Web App)</h1>

<p align="center">
  A clean, modern web dashboard to track monthly income and expenses — built with Flask and local JSON storage.
</p>

---
<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/flask-3.0+-black?style=flat-square&logo=flask" alt="Flask" />
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/NHasan143/monthly-expenses-tracker?style=flat-square" alt="License" />
  </a>
  <a href="https://github.com/NHasan143/monthly-expenses-tracker/stargazers">
    <img src="https://img.shields.io/github/stars/NHasan143/monthly-expenses-tracker?style=flat-square" alt="GitHub stars" />
  </a>
  <a href="https://github.com/NHasan143/monthly-expenses-tracker/network/members">
    <img src="https://img.shields.io/github/forks/NHasan143/monthly-expenses-tracker?style=flat-square" alt="GitHub forks" />
  </a>
  <a href="https://github.com/NHasan143/monthly-expenses-tracker/issues">
    <img src="https://img.shields.io/github/issues/NHasan143/monthly-expenses-tracker?style=flat-square" alt="GitHub issues" />
  </a>
</p>

## 📌 Overview

**Monthly Expenses Tracker (Web)** is a **Flask-based web application** that provides a modern admin dashboard for managing monthly budgets.
It is a full migration of the original Python CLI tool into a browser-based interface — no databases or external services required.

This project demonstrates:
- Flask web application structure (Blueprint, app factory pattern)
- Jinja2 templating with a shared base layout
- File-based data persistence (JSON)
- Separation of concerns: routes, data logic, templates, and static assets

---

## ✨ Features

- 📊 Live dashboard with stat cards and a spending doughnut chart
- ➕ Add, edit, and delete expenses via modal forms
- 🗂️ Category-based spending breakdown with progress bars
- 💰 Savings rate calculation
- 📥 Export full summary to CSV
- ⚙️ Settings page to update salary and reset all data
- 🎨 Dark theme UI with no external CSS framework dependencies

---

## 🧰 Tech Stack Used

- **Backend:** Python, Flask 3.0+
- **Templating:** Jinja2
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Charts:** Chart.js (CDN)
- **Data Storage:** JSON (local filesystem)

---

## 🚀 Getting Started (Local Setup)

### 🛠️ Prerequisites
- Python 3.8+ installed

### 📦 Installation

```bash
git clone https://github.com/NHasan143/monthly-expenses-tracker.git
cd monthly-expenses-tracker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the development server:

```bash
python run.py
```

Then open your browser and go to:

```
http://localhost:5000
```

> ⚠️ If port 5000 is in use change the port in `run.py`:
> ```python
> app.run(debug=True, port=5001)
> ```

---

## 🗂️ Project Structure

```text
monthly-expenses-tracker/
├── run.py                        # App entry point
├── requirements.txt              # Python dependencies
├── budget_data.json              # Local data storage (auto-created)
└── app/
    ├── __init__.py               # Flask app factory
    ├── routes.py                 # All URL routes (Blueprint)
    ├── data.py                   # Data logic: load, save, calculate
    ├── templates/
    │   ├── base.html             # Shared layout (sidebar, topbar, flash messages)
    │   ├── dashboard.html        # Stat cards, chart, recent expenses
    │   ├── expenses.html         # Full expense table with edit/delete
    │   └── settings.html        # Salary update, CSV export, data reset
    └── static/
        ├── css/
        │   └── main.css          # All styles (variables, layout, components)
        └── js/
            ├── modals.js         # Shared modal open/close logic
            ├── dashboard.js      # Chart.js doughnut chart
            └── expenses.js       # Edit modal population
```

---

## 💾 Data Storage

This project uses a local JSON file (`budget_data.json`) to store income and expenses.
All financial data is kept on your machine, making the application:

- Easy to reset (delete the JSON file and restart)
- Transparent and portable
- Suitable for fully offline use

---

## 📄 Pages

| Route | Page | Description |
|---|---|---|
| `/` | Dashboard | Overview with stats, chart, and recent expenses |
| `/expenses` | Expenses | Full table with add, edit, and delete |
| `/settings` | Settings | Update salary, export CSV, reset all data |
| `/export` | — | Downloads `budget_export.csv` directly |

---

## 🔮 Roadmap & Future Enhancements

- [Added] Flask web interface dashboard
- [Added] Spending breakdown by category with chart
- [Added] Edit existing expenses
- [Added] Export summary to CSV
- [Added] Savings rate calculation
- [ ] User authentication (login/logout)
- [ ] Monthly history (track across multiple months)
- [ ] Mobile responsive layout
- [ ] Dark/light theme toggle

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-change`
3. Commit changes: `git commit -m "Add my change"`
4. Push: `git push origin feature/my-change`
5. Open a Pull Request

---

## 📄 License

Licensed under the MIT License. See [LICENSE](./LICENSE).

---

## 👤 Author

**Naymul Hasan**
GitHub: https://github.com/NHasan143