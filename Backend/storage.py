import csv
from models import Expense
from pathlib import Path

CSV_FILE = Path("expense.csv")

#To check header present or not meow
if not CSV_FILE.exists():
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["amount", "category", "description", "date"])

def add_expense(expense: Expense):
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([expense.amount. expense.category, expense.description, expense.date])
    return {"message": "Expense added successfully"}

def get_all_expenses():
    with open(CSV_FILE, mode="r") as f:
        reader = csv.DictReader(f)
        return list(reader)