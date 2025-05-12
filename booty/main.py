from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from calculator import (
    run_payroll_waste,
    run_customer_churn,
    run_leadership_drag,
    run_productivity_dive,
    run_workforce_productivity
)

app = FastAPI()

class PayrollWasteRequest(BaseModel):
    industry: str
    total_employees: int
    avg_salary: float
    improvement_rate: float

class CustomerChurnRequest(BaseModel):
    industry: str
    num_customers: int
    avg_revenue: float
    cac: float
    churn_rate: float
    desired_improvement: float

class LeadershipDragRequest(BaseModel):
    industry: str
    total_employees: int
    avg_salary: float
    leadership_drag: float

class ProductivityDiveRequest(BaseModel):
    industry: str
    total_employees: int
    avg_salary: float
    absenteeism_days: float
    avg_hours: float

class WorkforceProductivityRequest(BaseModel):
    industry: str
    total_revenue: float
    payroll_cost: float
    num_employees: int
    productive_hours: float
    target_hours_per_employee: float
    absenteeism_days: float
    overtime_hours: Optional[float] = Field(default=None)

@app.post("/run-payroll-waste")
def run_payroll_waste_route(request: PayrollWasteRequest):
    return run_payroll_waste(request)

@app.post("/run-churn-calculator")
def run_customer_churn_route(request: CustomerChurnRequest):
    return run_customer_churn(request)

@app.post("/run-leadership-drag-calculator")
def run_leadership_drag_route(request: LeadershipDragRequest):
    return run_leadership_drag(request)

@app.post("/run-productivity-dive")
def run_productivity_dive_route(request: ProductivityDiveRequest):
    return run_productivity_dive(request)

@app.post("/run-workforce-productivity")
def run_workforce_productivity_route(request: WorkforceProductivityRequest):
    return run_workforce_productivity(request)
