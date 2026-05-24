from fastapi import FastAPI, HTTPException
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel

app = FastAPI()
class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date : date
    end_date : date

@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date):
    expenses = db_helper.fetch_expense_for_date(expense_date)

    return expenses

@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses:List[Expense]):
    db_helper.delete_expense_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)

    return{"message":"Expenses updated sucessfully"}

@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code = 500, details="Failed to retrive expense summary from the database")
    total = sum(row['total'] for row in data)

    breakdown = {}
    for row in data:
        percentage = (row['total']/total)*100 if total != 0 else 0
        breakdown[row['category']] = {
            "total": row['total'],
            "percentage": round(percentage, 2)
        }
    return breakdown



@app.post("/analytics_month/")
def get_analytics_month():
    data = db_helper.fetch_expense_monthwise()
    if data is None:
        raise HTTPException(status_code = 500, details="Failed to retrive expense summary from the database")
    total = sum(row['total'] for row in data)

    breakdown = {}
    for row in data:
        breakdown[row['month']] = {
            "total": row['total']
        }
    return breakdown

