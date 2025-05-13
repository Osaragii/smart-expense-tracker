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
    expense_id = get_next_id
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([expense_id, expense.amount. expense.category, expense.description, expense.date])
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
        writer = csv.DictWriter(f, fieldnames=["id", "amount", "category", "desceription", "date"])
        writer.writeheader()
        writer.writerows(updated_rows)

    return {"message": "Expense deleted"}
