from pydantic import BaseModel
from datetime import date
from typing import Optional

class Expense(BaseModel):
    amount: float
    category: str
    description: str
    date: date

class NLPExpenseRequest(BaseModel):
    text: str

class ExtractedExpenseData(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    confidence: float = 0.0
    raw_text: str