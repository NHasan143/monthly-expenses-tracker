import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Initialize the rich console object for all output
console = Console()

# --- Data Handling Functions ---

def load_data():
    """Load salary and expenses from a file, or initialize if file doesn't exist."""
    data_file = 'budget_data.json'
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            console.print("[bold red]Error reading data file. Initializing new data.[/bold red]")
    return {"salary": 0.0, "expenses": []}

def save_data(data):
    """Save salary and expenses to a file."""
    with open('budget_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def calculate_balance(salary, expenses):
    """Calculate remaining balance."""
    total_expenses = sum(expense['amount'] for expense in expenses)
    return salary - total_expenses

def reset_data():
    """Deletes the budget data file to reset all saved memory."""
    data_file = 'budget_data.json'
    if os.path.exists(data_file):
        try:
            os.remove(data_file)
            console.print("✅ [bold green]All saved budget data has been successfully deleted.[/bold green]")
            return {"salary": 0.0, "expenses": []}
        except OSError as e:
            console.print(f"[bold red]Error: Could not delete the data file: {e}[/bold red]")
            return load_data()
    else:
        console.print("[yellow]Data file not found. Nothing to reset.[/yellow]")
        return {"salary": 0.0, "expenses": []}

# --- Menu and Feature Functions ---

def display_menu():
    """Display the main menu options."""
    menu = Panel(
        "[bold cyan]1.[/bold cyan] Update Your Monthly Salary\n" 
        "[bold cyan]2.[/bold cyan] Add New Expense\n"
        "[bold cyan]3.[/bold cyan] View Full Dashboard\n"
        "[bold cyan]4.[/bold cyan] Reset All Data ([bold red]Caution![/bold red])\n"
        "[bold cyan]5.[/bold cyan] Exit Application",
        title="[bold yellow]Main Menu[/bold yellow]",
        border_style="blue",
        width=70
    )
    console.print(menu)

def add_new_expense(data):
    """Prompts user to repeatedly add new expenses with categories until they say no."""
    console.print("\n[bold magenta]-- Add Expense(s) --[/bold magenta]")
    
    while True:
        # Prompt to continue adding expenses
        continue_adding = console.input("Add a new expense? ([green]y[/green]/[red]n[/red]): ").lower()
        
        if continue_adding in ('n', 'no'):
            break

        try:
            description = console.input("Enter expense description: ")
            category = console.input("Enter expense category (e.g., Rent, Groceries): ")
            amount = float(console.input("Enter expense amount: $"))
            
            if amount <= 0:
                console.print("[yellow]Expense amount must be positive. Try again.[/yellow]")
                continue
                
            data["expenses"].append({
                "description": description, 
                "amount": amount, 
                "category": category
            })
            save_data(data)
            console.print("[green]✅ Expense added successfully![/green]")
            
        except ValueError:
            console.print("[bold red]Please enter a valid number for the expense amount. Try again.[/bold red]")
            
    console.print("[dim]Finished adding expenses. Returning to main menu...[/dim]")

def update_salary(data):
    """Prompts user to update the monthly salary."""
    console.print("\n[bold magenta]--- Update Salary ---[/bold magenta]")
    
    try:
        current_salary = data.get("salary", 0.0)
        console.print(f"Current salary is [green]${current_salary:.2f}[/green].")
        salary_input = console.input("Enter new monthly salary: $")
        new_salary = float(salary_input)
        
        if new_salary < 0:
            console.print("[yellow]Salary cannot be negative.[/yellow]")
            return
            
        data["salary"] = new_salary
        save_data(data)
        console.print(f"[green]✅ Salary updated to ${new_salary:.2f}[/green]")
        
    except ValueError:
        console.print("[bold red]Please enter a valid number.[/bold red]")


def display_dashboard(data):
    """Calculates and displays the rich-formatted dashboard summary with categories."""
    salary = data["salary"]
    expenses = data["expenses"]
    
    # 1. Calculate Totals (Logic unchanged)
    total_expenses = sum(expense['amount'] for expense in expenses)
    balance = calculate_balance(salary, expenses)
    balance_style = "bold green" if balance >= 0 else "bold red"

    console.print("\n[bold yellow]--- CURRENT BUDGET DASHBOARD ---[/bold yellow]")

    # 2. Expense Table (WIDTH ADDED)
    expense_table = Table(
        title="Expense Breakdown", 
        show_header=True, 
        header_style="bold magenta",
        width=70  # <-- NEW: Fixed width added here
    )
    expense_table.add_column("Description", style="dim", min_width=20)
    expense_table.add_column("Category", style="yellow", min_width=15)
    expense_table.add_column("Amount", justify="right", style="cyan")

    if expenses:
        for expense in expenses:
            category_name = expense.get('category', '[Uncategorized]')
            expense_table.add_row(
                expense['description'], 
                category_name, 
                f"${expense['amount']:.2f}"
            )
    else:
        expense_table.add_row("[italic]No expenses recorded.[/italic]", "", "")

    console.print(expense_table)
    
    # 3. Category-wise Summary Logic (Logic unchanged)
    category_totals = {}
    for expense in expenses:
        category = expense.get('category', '[Uncategorized]')
        amount = expense['amount']
        category_totals[category] = category_totals.get(category, 0.0) + amount

    category_list = ""
    if category_totals:
        for category, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
            category_list += f"  - [italic]{category}:[/italic] ${total:.2f}\n"
    else:
        category_list = "  [italic]No categories recorded.[/italic]\n"
    
    # 4. Final Summary Panel (WIDTH ADDED)
    summary_content = (
        f"[bold white]Monthly Salary:[/bold white] [green]${salary:.2f}[/green]\n"
        f"[bold white]Total Expenses:[/bold white] [red]${total_expenses:.2f}[/red]\n"
        f"---"
        f"[{balance_style}]\nRemaining Balance: ${balance:.2f}[/{balance_style}]\n"
        f"\n[bold underline]Spending by Category:[/bold underline]\n"
        f"{category_list}"
    )
    
    console.print(Panel(
        summary_content, 
        title="[bold yellow]💰 Budget Overview[/bold yellow]", 
        border_style="blue",
        padding=(1, 2),
        width=70  # <-- NEW: Fixed width added here
    ))


# --- Main Application Loop ---

def run_app():
    """Main function containing the menu loop."""
    console.print("[bold cyan]=== Welcome to the Monthly Budget Tracker ===[/bold cyan]")
    data = load_data()
    
    while True:
        display_dashboard(data)
        display_menu()

        choice = console.input("Enter your option (1-5): ")
        
        if choice == '1':
            update_salary(data) 
        elif choice == '2':
            add_new_expense(data) 
        elif choice == '3':
            console.print("[dim]Dashboard refreshed.[/dim]")
            pass 
        elif choice == '4':
            data = reset_data()
        elif choice == '5':
            console.print("[bold red]👋 Thanks for using the Expenses Tracker. Good Luck![/bold red]")
            break
        else:
            console.print("[bold red]Invalid choice. Please enter a number between 1 and 5.[/bold red]")
        
        console.input("\n[dim]Press Enter to return to the menu...[/dim]") 
        console.clear() 

if __name__ == "__main__":
    run_app()