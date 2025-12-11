# 💰 Monthly Budget Tracker

A lightweight, Python-based Command Line Interface (CLI) application designed to help users track their monthly salary, log expenses, and calculate their remaining balance. The application uses JSON for persistent data storage, ensuring your records remain saved between sessions.

## 📋 Features

* **Persistent Data Storage:** Automatically saves your salary and expenses to a local `budget_data.json` file.
* **Salary Management:** Set your monthly salary and update it whenever necessary.
* **Expense Logging:** Add multiple expenses with descriptions and amounts in a single session.
* **Input Validation:** Robust error handling ensures that non-numeric inputs or negative numbers do not crash the application.
* **Financial Summary:** Instantly calculates total expenses and remaining balance.

## 🛠️ Prerequisites

* **Python 3.x** installed on your machine.
    * No external libraries are required (uses standard `os` and `json` libraries).

## 🚀 Getting Started

1.  **Clone the Repository** (or download the source code):
    ```bash
    git clone [https://github.com/NHasan143/budget-tracker.git](https://github.com/NHasan143/budget-tracker.git)
    cd budget-tracker
    ```

2.  **Run the Application:**
    Navigate to the project directory and run the script:
    ```bash
    python budget_tracker.py
    ```

## 💻 Usage Example

When you run the program, you will be guided through an interactive prompt. Here is what a typical session looks like:

```text
=== Monthly Budget Tracker ===
Enter your monthly salary: $ 3000

Add a new expense? (y/n): y
Enter expense description: Rent
Enter expense amount: $ 1200

Add a new expense? (y/n): y
Enter expense description: Groceries
Enter expense amount: $ 350

Add a new expense? (y/n): n

=== Budget Summary ===
Monthly Salary: $3000.00
Expenses:
  - Rent: $1200.00
  - Groceries: $350.00
Total Expenses: $1550.00
Remaining Balance: $1450.00

🧩 How It Works

The application follows a linear logic flow to ensure data integrity. When the script is executed, it first attempts to load existing data. If none exists, it initializes a new profile.

📂 Data Structure

Your data is stored locally in budget_data.json. This allows the program to remember your salary and previous expenses the next time you run it.

Example budget_data.json:

{
    "salary": 3000.0,
    "expenses": [
        {
            "description": "Rent",
            "amount": 1200.0
        },
        {
            "description": "Groceries",
            "amount": 350.0
        }
    ]
}

🔮 Future Improvements

    [ ] Add categories for expenses (e.g., Food, Transport, Utilities).

    [ ] Add the ability to delete specific expenses.

    [ ] Export summary to a .csv or .txt file.

    [ ] Visualize spending with a pie chart.

📄 License

This project is open-source and available under the MIT License.

Created by Naymul Hasan