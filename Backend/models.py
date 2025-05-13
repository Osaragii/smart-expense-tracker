from pydantic import BaseModel
from datetime import date

class Expense(BaseModel):
    id: int
    amount: float
    category: str
    description: str
    date: date
