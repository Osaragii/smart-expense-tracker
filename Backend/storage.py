import csv
from models import Expense
from pathlib import Path
from typing import List, Optional, Union
from datetime import datetime

# Optional: Use FileLock for concurrency-safe file operations
# from filelock import FileLock

CSV_FILE = Path("expenses.csv")
CSV_HEADERS = ["id", "amount", "category", "description", "date"]
DATE_FORMAT = "%Y-%m-%d"  # Adjust if your dates are stored differently

def initialize_csv():
    if not CSV_FILE.exists():
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

initialize_csv()

def get_next_id() -> int:
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

def add_expense(expense: Expense) -> dict:
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

def get_all_expenses() -> List[dict]:
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expenses = []
            for row in reader:
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

def delete_expense(expense_id: int) -> dict:
    try:
        updated_rows = []
        deleted = False
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if int(row["id"]) != expense_id:
                        updated_rows.append(row)
                    else:
                        deleted = True
                except (ValueError, KeyError):
                    continue

        if not deleted:
            return {"error": "Expense not found"}

        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(updated_rows)

        return {"message": "Expense deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete expense: {str(e)}"}

def update_expense(expense_id: int, updated_expense: Expense) -> dict:
    try:
        updated_rows = []
        found = False
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
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
                except (ValueError, KeyError):
                    continue

        if not found:
            return {"error": "Expense not found"}

        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(updated_rows)

        return {"message": "Expense updated successfully"}
    except Exception as e:
        return {"error": f"Failed to update expense: {str(e)}"}

def get_filtered_expenses(
    category: Optional[str] = None,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    search: Optional[str] = None
) -> List[dict]:
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, DATE_FORMAT)
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, DATE_FORMAT)

        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            filtered = []

            for row in reader:
                if not row.get("id"):
                    continue

                # Category filter
                if category and row.get("category", "").lower() != category.lower():
                    continue

                # Date filter
                try:
                    row_date = datetime.strptime(row["date"], DATE_FORMAT)
                    if start_date and row_date < start_date:
                        continue
                    if end_date and row_date > end_date:
                        continue
                except (ValueError, KeyError):
                    continue

                # Search filter
                if search and search.lower() not in row.get("description", "").lower():
                    continue

                filtered.append(row)

            return filtered
    except FileNotFoundError:
        initialize_csv()
        return []
