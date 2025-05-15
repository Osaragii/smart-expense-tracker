from fastapi import FastAPI, HTTPException
from typing import Optional
from datetime import date
from models import Expense
from storage import (
    add_expense, 
    get_all_expenses, 
    get_filtered_expenses,  
    delete_expense, 
    update_expense
)

app = FastAPI()

@app.post("/add-expense")
def createExpense(expense: Expense):
    return add_expense(expense)

@app.get("/expenses")
def readExpenses(
    category: Optional[str] = None, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None, 
    search: Optional[str] = None
):
    if category or start_date or end_date or search:
        return get_filtered_expenses(category, start_date, end_date, search)
    return get_all_expenses()

@app.delete("/delete-expense/{expense_id}")
def removeExpense(expense_id: int):
    result = delete_expense(expense_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.put("/update-expense/{expense_id}")
def modifyExpense(expense_id: int, updated_expense: Expense):
    result = update_expense(expense_id, updated_expense)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result