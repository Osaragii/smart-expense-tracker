from fastapi import FastAPI, HTTPException
from models import Expense
from storage import add_expense, get_all_expenses, delete_expense, update_expense

app = FastAPI()

@app.post("/add-expense")
def createExpense(expense: Expense):
    return add_expense(expense)

@app.get("/expenses")
def readExpenses():
    return get_all_expenses()

@app.delete("/delete-expense/{expense_id}")
def remove_expense(expense_id: int):
    result = delete_expense(expense_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result