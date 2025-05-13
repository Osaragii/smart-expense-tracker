from pydantic import BaseModel
from datetime import date

class Expense(BaseModel):
    amount: float
    category: str
    description: str
    date: date
