from fastapi import FastAPI
from models import Expense
from storage import add_expense, get_all_expenses

app = FastAPI()

@app.post("/add-expense")
def createExpense(expense: Expense):
    return add_expense(expense)

@app.get("/expenses")
def readExpenses():
    return get_all_expenses()