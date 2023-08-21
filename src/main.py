import click
from getpass import getpass
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine,func
from models import User, Transaction, Budget
import datetime
import bcrypt

# Global variable to track the authenticated user
authenticated_user = None

Session = sessionmaker(bind=create_engine("sqlite:///budget_tracker.db"))

  

@click.command()
def register_user():
    """User registration functionality."""
    username = click.prompt(click.style("Enter your username", fg="cyan"))
    password = getpass(click.style("Enter your password:", fg="cyan"))
    email = click.prompt(click.style("Enter your email", fg="cyan"))

    session = Session()
    existing_user = session.query(User).filter_by(username=username).first()

    if existing_user is not None:
        click.echo("Username already exists. Please log in or choose a different username.")
        session.close()
        return

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, password_hash=hashed_password, email=email)
    session.add(new_user)
    session.commit()
    session.close()

    click.echo(click.style("Registration successful.", fg="green"))
    main()  # Redirect to the login functionality after successful registration


@click.command()
def login():
    """Login functionality."""
    username = click.prompt(click.style("Enter your username", fg="cyan"))
    password = getpass(click.style("Enter your password:", fg="cyan"))

    session = Session()
    user = session.query(User).filter_by(username=username).first()

    if user is None:
        click.echo(click.style("User not found. Please register first.", fg="red"))
        session.close()
        main()
        return

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        
        click.echo(click.style("Incorrect password. Please try again.", fg="red"))
        session.close()
        main()
        return

    # Store the authenticated user's information in the session or as a global variable
    global authenticated_user
    authenticated_user = user

    click.echo(click.style("Login successful.", fg="green"))
    show_user_menu()  # Show the user menu directly after successful login


#user and login interface

def print_menu():
    click.echo(click.style("-------------------", fg="yellow", bold=True))
    click.echo(click.style("Budget Tracker CLI", fg="yellow", bold=True))
    click.echo(click.style("-------------------", fg="yellow", bold=True))
    click.echo(click.style("1. Register", fg="cyan"))
    click.echo(click.style("2. Login", fg="cyan"))

def print_user_menu():
    click.echo(click.style(f"Welcome, {authenticated_user.username}! 😄", fg="cyan", bold=True))
    session = Session()
    total_income = session.query(func.sum(Transaction.amount)).filter_by(user_id=authenticated_user.id, transaction_type='income').scalar() or 0
    total_expenses = session.query(func.sum(Transaction.amount)).filter_by(user_id=authenticated_user.id, transaction_type='expense').scalar() or 0
    balance = total_income - total_expenses
    session.close()
    click.echo(click.style("-----------------------------", fg="yellow", bold=True))
    click.echo(click.style(f"Available Balance: {balance}", fg="green", bold=True))
    click.echo(click.style("-----------------------------", fg="yellow", bold=True))
    click.echo(click.style("1. Add a transaction", fg="bright_magenta"))
    click.echo(click.style("2. View all transactions", fg="bright_magenta"))
    click.echo(click.style("3. Delete a transaction", fg="bright_magenta"))
    click.echo(click.style("4. Set budget", fg="bright_magenta"))
    click.echo(click.style("5. View all budgets", fg="bright_magenta"))
    click.echo(click.style("6. Delete budget", fg="bright_magenta"))
    click.echo(click.style("7. Generate report", fg="bright_magenta"))
    click.echo(click.style("8. Logout", fg="bright_magenta"))
    click.echo(click.style("9. Exit", fg="bright_magenta"))

def show_user_menu():
    
    while True:
        print_user_menu()
        choice = click.prompt(click.style("Enter your choice (1-8): ", fg="yellow"))

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            delete_transaction()
        elif choice == "4":
            set_budget()
        elif choice == "5":
            view_budget()
        elif choice == "6":
             delete_budget()
        elif choice == "7":
            generate_report()
        
        elif choice == "8":
            logout()
            break  # Exit the user menu and return to the main menu
        elif choice == "9":
            exit_program()
        else:
            
            click.echo(click.style("Invalid choice. Please try again.", fg="red"))



def add_transaction():
    if authenticated_user is None:
        click.echo(click.style("Please login first.", fg="red"))
        return
    
    click.echo(click.style("Add a new transaction:", fg="cyan"))
    try:
        transaction_type = click.prompt(click.style("Type (income/expense): ", fg="cyan"))
        category = click.prompt(click.style("Category: ", fg="cyan"))
        amount_str = click.prompt(click.style("Amount: ", fg="cyan"))
        amount = float(amount_str.replace(",", ""))
        date_str = click.prompt(click.style("Date (YYYY-MM-DD): ", fg="cyan"))
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        transaction = Transaction(transaction_type=transaction_type, category=category, amount=amount, date=date, user_id=authenticated_user.id)
        session = Session()
        session.add(transaction)
        session.commit()
        session.close()

        click.echo("Transaction added successfully!")
    except ValueError:
        click.echo(click.style("Invalid input format. Please try again.", fg="red"))

    show_user_menu()

def view_transactions():
    if authenticated_user is None:
        click.echo(click.style("Please login first.", fg="red"))
        return
    
    
    click.echo(click.style("*********************", fg="yellow"))
    click.echo(click.style("Viewing all transactions:", fg="cyan"))
    click.echo(click.style("*********************", fg="yellow"))
    
    session = Session()
    transactions = session.query(Transaction).filter_by(user_id=authenticated_user.id).all()
    session.close()

    if not transactions:
        click.echo(click.style("No transactions found ,please add one.", fg="red"))
        return

    for transaction in transactions:
        click.echo(click.style(f"ID: {transaction.id}", fg="cyan"))
        click.echo(click.style(f"Type: {transaction.transaction_type}", fg="cyan"))
        click.echo(click.style(f"Category: {transaction.category}", fg="cyan"))
        click.echo(click.style(f"Amount: {transaction.amount}", fg="cyan"))
        click.echo(click.style(f"Date: {transaction.date}", fg="cyan"))
        click.echo(click.style("------------------------", fg="yellow"))
        
        

def delete_transaction():
    """Delete a transaction from the database."""
    session = Session()
    transactions = session.query(Transaction).filter_by(user_id=authenticated_user.id).all()

    if not transactions:
        click.echo(click.style("No transactions found.", fg="yellow"))
        session.close()
        show_user_menu()
        return

    click.echo("Available transactions:")
    for transaction in transactions:
        click.echo(f"Transaction ID: {transaction.id} | Amount: {transaction.amount} | Category: {transaction.category}")

    transaction_id = click.prompt(click.style("Enter the ID of the transaction you want to delete", fg="cyan"))

    transaction = session.query(Transaction).filter_by(user_id=authenticated_user.id, id=transaction_id).first()
    if transaction is None:
        click.echo(click.style("Transaction not found.", fg="red"))
        session.close()
        show_user_menu()
        return

    session.delete(transaction)
    session.commit()
    session.close()

    click.echo(click.style("Transaction deleted successfully.", fg="green"))
    show_user_menu()


def set_budget():
    """Set the budget for the authenticated user."""
    if authenticated_user is None:
        click.echo(click.style("Please login first.", fg="red"))
        return

    click.echo(click.style("Set Budget:", fg="cyan"))
    category = click.prompt(click.style("Enter the budget category: ", fg="cyan"))
    amount_str = click.prompt(click.style("Enter the budget amount: ", fg="cyan"))
    amount = float(amount_str.replace(",", ""))

    session = Session()
    existing_budget = session.query(Budget).filter_by(user_id=authenticated_user.id, category=category).first()

    if existing_budget:
        existing_budget.amount = amount
        click.echo(click.style("Budget updated successfully.", fg="green"))
    else:
        new_budget = Budget(user_id=authenticated_user.id, category=category, amount=amount)
        session.add(new_budget)
        click.echo(click.style("Budget set successfully.", fg="green"))

    session.commit()
    session.close()
    
def view_budget():
    """View the budget for the authenticated user."""
    if authenticated_user is None:
        click.echo(click.style("Please login first.", fg="red"))
        return

    session = Session()
    budgets = session.query(Budget).filter_by(user_id=authenticated_user.id).all()

    if budgets:
        click.echo(click.style("viewing all Budgets:", fg="cyan"))
        for budget in budgets:
            click.echo(click.style(f"ID: {budget.id}, Category: {budget.category}, Amount: {budget.amount}", fg="cyan"))
    else:
        click.echo(click.style("No budgets found. Please add one", fg="cyan"))

    session.close()

def delete_budget():
    """Delete a budget."""
    session = Session()
    budgets = session.query(Budget).filter_by(user_id=authenticated_user.id).all()

    if not budgets:
        click.echo(click.style("No budgets found.", fg="yellow"))
        session.close()
        show_user_menu()
        return
    click.echo("Available budgets:")
    for budget in budgets:
        click.echo(f"Budget ID: {budget.id} | Category: {budget.category} | Amount: {budget.amount}")

    budget_id = click.prompt(click.style("Enter the ID of the budget you want to delete", fg="cyan"))

    budget = session.query(Budget).filter_by(id=budget_id).first()
    if budget is None:
        click.echo(click.style("Budget not found.", fg="red"))
        session.close()
        show_user_menu()
        return

    session.delete(budget)
    session.commit()
    session.close()

    click.echo(click.style("Budget deleted successfully.", fg="green"))
    show_user_menu()

    
@click.option("--user-id", type=int, help="User ID for generating the report")
def generate_report(user_id=None):
    """Generate a report of transactions and budgets for a specific user."""
    if authenticated_user is None:
        click.echo(click.style("Please login first.", fg="red"))
        return

    if user_id is not None and user_id != authenticated_user.id:
        click.echo(click.style("You are not authorized to access this report.", fg="red"))
        return

    session = Session()
    if user_id is None:
        transactions = session.query(Transaction).filter_by(user_id=authenticated_user.id).all()
        budgets = session.query(Budget).filter_by(user_id=authenticated_user.id).all()
        click.echo(click.style(f"Report for User ID: {authenticated_user.id}", fg="cyan"))
    else:
        transactions = session.query(Transaction).filter_by(user_id=user_id).all()
        budgets = session.query(Budget).filter_by(user_id=user_id).all()
        click.echo(click.style(f"Report for User ID: {user_id}", fg="cyan"))
    session.close()

    if not transactions and not budgets:
        click.echo(click.style("No transactions or budgets made.", fg="red"))
        return

    if transactions:
        click.echo(click.style("Transactions:", fg="cyan"))
        for transaction in transactions:
            click.echo(f"ID: {transaction.id}")
            click.echo(f"Type: {transaction.transaction_type}")
            click.echo(f"Category: {transaction.category}")
            click.echo(f"Amount: {transaction.amount}")
            click.echo(f"Date: {transaction.date}")
            click.echo("------------------------")
    else:
        click.echo("No transactions found.")

    if budgets:
        click.echo(click.style("Budgets:", fg="cyan"))
        for budget in budgets:
            click.echo(f"ID: {budget.id}")
            click.echo(f"Category: {budget.category}")
            click.echo(f"Amount: {budget.amount}")
            click.echo("------------------------")
    else:
        click.echo("No budgets found.")


def logout():
    """Logout the authenticated user."""
    global authenticated_user
    authenticated_user = None
    click.echo(click.style("Logged out successfully.", fg="green"))
    main() # returns to the menu

def exit_program():
    """Exit the program."""
    click.echo(click.style("Exiting the Budget Tracker CLI.",fg="blue", bold=True))
    raise SystemExit



def main():
   

    while True:
       
        print_menu()
        choice = click.prompt(click.style("Enter your choice (1-2): ", fg="yellow"))

        if choice == "1":
            register_user()
        elif choice == "2":
            login()
            if authenticated_user is not None:
                show_user_menu()  # Show the user menu if login is successful
            break  # Exit the main loop after successful login
        else:
            click.echo(click.style("Invalid choice. Please try again.", fg="red"))
if __name__ == "__main__":
    main()
