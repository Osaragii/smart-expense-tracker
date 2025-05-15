import csv
from models import Expense
from pathlib import Path

CSV_FILE = Path("expense.csv")

#To check header present or not meow
if not CSV_FILE.exists():
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "amount", "category", "description", "date"])

#To generate id for new items meowmeow
def get_next_id():
    try:
        with open(CSV_FILE, mode="r") as f:
            reader = csv.DictReader(f)
            ids = [int(row["id"]) for row in reader]
            return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        return 1

#Add feature meow
def add_expense(expense: Expense):
    expense_id = get_next_id()
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([expense_id, expense.amount, expense.category, expense.description, expense.date])
    return {"message": "Expense added", "id": expense_id}

#To read all expenses meow
def get_all_expenses():
    with open(CSV_FILE, mode="r") as f:
        reader = csv.DictReader(f)
        return list(reader)
    
#Delete feature meow
def delete_expense(expense_id: int):
    updated_rows = []
    deleted = False
    with open(CSV_FILE, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id"]) != expense_id:
                updated_rows.append(row)
            else:
                deleted = True
    
    if not deleted:
        return {"error": "Expense not found"}

    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "amount", "category", "description", "date"])
        writer.writeheader()
        writer.writerows(updated_rows)

    return {"message": "Expense deleted"}

#For updating expenses meow meow meow
def update_expense(expense_id: int, updated_expense: Expense):
    updated_rows = []
    found = False
    with open(CSV_FILE, mode="r") as f:
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
        
        with open(CSV_FILE, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "amount", "category", "description", "date"])
            writer.writeheader()
            writer.writerrows(updated_rows)

        return {"message": "Expense updated"}

#Filter Expenses
def get_filtered_expenses(category=None, start_date=None, end_date=None, search=None):
    with open(CSV_FILE, mode="r") as f:
        reader = csv.DictReader(f)
        filtered = []

        for row in reader:
            if category and row["category"].lower() != category.lower():
                continue

            if start_date and row["date"] < str(start_date):
                continue

            if end_date and row["date"] > str(end_date):
                continue

            if search and search.lower() not in row["description"].lower():
                continue

            filtered.append(row)

    return filtered