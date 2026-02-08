<h1 align="center"> 💰 Monthly Expenses Tracker (Python CLI)</h1>

<p align="center">
  A simple Python CLI tool to track monthly income and expenses using local JSON storage.
</p>

---
<p align="center">
  </a>
    <img src="https://img.shields.io/badge/python-3.8+-blue?style=flat-square" alt="Python" />
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/NHasan143/monthly-expenses-tracker?style=flat-square" alt="License" />
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

**Monthly Expenses Tracker** is a **Python CLI-based expense tracker** that helps users manage monthly budgets by recording income and expenses locally.  
It is ideal for developers who want a **simple, offline personal finance tool** without databases or external services.

This project demonstrates:
- Python fundamentals
- File-based data persistence (JSON)
- Command-line application design

---

## ✨ Features

- Track monthly income (salary)
- Add, categorize, and store expenses
- Calculate total expenses and remaining balance
- Persistent local storage using JSON files
- Lightweight and dependency-free

---

## 🧰 Tech Stack Used

- **Programming Language:** Python
- **Application Type:** Command-Line Interface (CLI)
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

```


---

## ▶️ Usage

Run the script:

```bash
python ExpensesTracker.py
```

Follow the prompts to:
- Enter salary
- Add expenses
- Modify Expenses
- View summary (spent + remaining)

---

## 🗂️ Project Structure

```text
monthly-expenses-tracker/
├─ ExpensesTracker.py
├─ README.md
└─ (data files: *.json)
```

---

## 💾 Data Storage

This project uses JSON files to store income and expenses locally.  
All financial data is stored using JSON files, making the application:

- Easy to reset
- Transparent
- Suitable for offline use

To reset all data, simply delete the JSON files and restart the program.

---

## 🔮 Roadmap & Future Enhancements

- [Added] Add categories for expenses (e.g., Food, Transport, Utilities).

- [Added] Add the ability to delete specific expenses.

- [Added] Export summary to a .csv or .txt file.

- [Working] Visualize spending with a pie chart.

- [ ] Add a web interface dashboard

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
