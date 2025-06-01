from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import date
from models import Expense, NLPExpenseRequest, ExtractedExpenseData
from storage import (
    add_expense, 
    get_all_expenses, 
    get_filtered_expenses,  
    delete_expense, 
    update_expense
)
from nlp_processor import nlp_processor

app = FastAPI(title="Smart Expense Tracker", description="NLP-powered expense tracking API")

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Smart Expense Tracker API", "status": "running"}

# NLP Endpoints
@app.post("/process-expense", response_model=ExtractedExpenseData)
def process_natural_language_expense(request: NLPExpenseRequest):
    """Process natural language expense text and extract structured data"""
    try:
        extracted_data = nlp_processor.process_expense_text(request.text)
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing expense text: {str(e)}")

@app.post("/add-smart-expense")
def add_smart_expense(request: NLPExpenseRequest):
    """Process natural language text and directly add expense"""
    try:
        # Extract data using NLP
        extracted_data = nlp_processor.process_expense_text(request.text)
        
        # Validate that we have minimum required data
        if not extracted_data.amount:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract amount from the text. Please specify an amount."
            )
        
        # Create expense object
        expense = Expense(
            amount=extracted_data.amount,
            category=extracted_data.category or 'miscellaneous',
            description=extracted_data.description or 'Expense',
            date=extracted_data.date or date.today()
        )
        
        # Add to storage
        result = add_expense(expense)
        
        # Return both the result and extracted data for frontend feedback
        return {
            "success": True,
            "expense_added": result,
            "extracted_data": extracted_data,
            "confidence": extracted_data.confidence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding smart expense: {str(e)}")

# Existing CRUD Endpoints
@app.post("/add-expense")
def create_expense(expense: Expense):
    """Manually add expense with structured data"""
    return add_expense(expense)

@app.get("/expenses")
def read_expenses(
    category: Optional[str] = None, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None, 
    search: Optional[str] = None
):
    """Get all expenses with optional filtering"""
    if category or start_date or end_date or search:
        return get_filtered_expenses(category, start_date, end_date, search)
    return get_all_expenses()

@app.delete("/delete-expense/{expense_id}")
def remove_expense(expense_id: int):
    """Delete an expense by ID"""
    result = delete_expense(expense_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.put("/update-expense/{expense_id}")
def modify_expense(expense_id: int, updated_expense: Expense):
    """Update an existing expense"""
    result = update_expense(expense_id, updated_expense)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# Analytics Endpoints
@app.get("/analytics/summary")
def get_expense_summary():
    """Get basic expense analytics"""
    try:
        expenses = get_all_expenses()
        
        if not expenses:
            return {"message": "No expenses found"}
        
        # Calculate totals
        total_amount = sum(float(expense['amount']) for expense in expenses)
        total_count = len(expenses)
        
        # Category breakdown
        category_totals = {}
        for expense in expenses:
            category = expense['category']
            amount = float(expense['amount'])
            category_totals[category] = category_totals.get(category, 0) + amount
        
        # Recent expenses (last 5)
        recent_expenses = expenses[-5:] if len(expenses) >= 5 else expenses
        
        return {
            "total_amount": round(total_amount, 2),
            "total_count": total_count,
            "average_expense": round(total_amount / total_count, 2),
            "category_breakdown": category_totals,
            "recent_expenses": recent_expenses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)