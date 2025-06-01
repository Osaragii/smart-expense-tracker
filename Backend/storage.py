import csv
from models import Expense
from pathlib import Path

CSV_FILE = Path("expenses.csv")

# Initialize CSV file with headers
def initialize_csv():
    if not CSV_FILE.exists():
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "amount", "category", "description", "date"])

# Initialize on import
initialize_csv()

def get_next_id():
    """Generate next available ID"""
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            ids = []
            for row in reader:
                try:
                    ids.append(int(row["id"]))
                except (ValueError, KeyError):
                    continue
            return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        initialize_csv()
        return 1

def add_expense(expense: Expense):
    """Add new expense to CSV"""
    try:
        expense_id = get_next_id()
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                expense_id, 
                expense.amount, 
                expense.category, 
                expense.description, 
                str(expense.date)
            ])
        return {"message": "Expense added successfully", "id": expense_id}
    except Exception as e:
        return {"error": f"Failed to add expense: {str(e)}"}

def get_all_expenses():
    """Read all expenses from CSV"""
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expenses = []
            for row in reader:
                # Clean and validate data
                if row.get("id") and row.get("amount"):
                    expenses.append({
                        "id": row["id"],
                        "amount": row["amount"],
                        "category": row["category"],
                        "description": row["description"],
                        "date": row["date"]
                    })
            return expenses
    except FileNotFoundError:
        initialize_csv()
        return []

def delete_expense(expense_id: int):
    """Delete expense by ID"""
    try:
        updated_rows = []
        deleted = False
        
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["id"]) != expense_id:
                    updated_rows.append(row)
                else:
                    deleted = True
        
        if not deleted:
            return {"error": "Expense not found"}

        # Rewrite file without deleted expense
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "amount", "category", "description", "date"])
            writer.writeheader()
            writer.writerows(updated_rows)

        return {"message": "Expense deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete expense: {str(e)}"}

def update_expense(expense_id: int, updated_expense: Expense):
    """Update existing expense"""
    try:
        updated_rows = []
        found = False
        
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["id"]) == expense_id:
                    updated_rows.append({
                        "id": expense_id,
                        "amount": updated_expense.amount,
                        "category": updated_expense.category,
                        "description": updated_expense.description,
                        "date": str(updated_expense.date)
                    })
                    found = True
                else:
                    updated_rows.append(row)
        
        if not found:
            return {"error": "Expense not found"}
        
        # Rewrite file with updated data
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "amount", "category", "description", "date"])
            writer.writeheader()
            writer.writerows(updated_rows)

        return {"message": "Expense updated successfully"}
    except Exception as e:
        return {"error": f"Failed to update expense: {str(e)}"}

def get_filtered_expenses(category=None, start_date=None, end_date=None, search=None):
    """Get filtered expenses based on criteria"""
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            filtered = []

            for row in reader:
                # Skip empty rows
                if not row.get("id"):
                    continue
                    
                # Category filter
                if category and row["category"].lower() != category.lower():
                    continue

                # Date filters
                if start_date and row["date"] < str(start_date):
                    continue

                if end_date and row["date"] > str(end_date):
                    continue

                # Search filter
                if search and search.lower() not in row["description"].lower():
                    continue

                filtered.append(row)

            return filtered
    except FileNotFoundError:
        initialize_csv()
        return []