from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from admin import admin_router
from calculator import (
    industry_benchmarks,
    calculate_customer_churn_loss,
    calculate_efficiency_loss_and_roi,
    calculate_leadership_drag_loss,
    calculate_productivity_metrics
)

# === App Setup ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jamescandoo.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

# === Input Models ===


class EfficiencyAutoInput(BaseModel):
    industry: str
    total_employees: conint(gt=0)
    avg_salary: confloat(gt=0)
    improvement_rate: confloat(gt=0, lt=100)


class ChurnCalculatorRequest(BaseModel):
    num_customers: conint(gt=0)
    churn_rate: confloat(gt=0, lt=100)
    avg_revenue: confloat(gt=0)
    cac: confloat(ge=0)
    desired_improvement: confloat(gt=0, lt=100)
    industry: str


class LeadershipDragCalculatorRequest(BaseModel):
    industry: str
    total_employees: conint(gt=0)
    avg_salary: confloat(gt=0)
    leadership_drag: confloat(gt=0, lt=100)


class ProductivityInput(BaseModel):
    industry: str
    total_revenue: confloat(gt=0)
    payroll_cost: confloat(gt=0)
    num_employees: conint(gt=0)
    productive_hours: confloat(gt=0)
    target_hours_per_employee: confloat(gt=0)
    overtime_hours: confloat(ge=0) = 0
    absenteeism_days: confloat(ge=0) = 0

# === API Endpoints ===


@app.post("/run-efficiency-calculator")
def run_efficiency_calculator(data: EfficiencyAutoInput):
    try:
        return calculate_efficiency_loss_and_roi(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-churn-calculator")
def run_churn_calculator(data: ChurnCalculatorRequest):
    try:
        return calculate_customer_churn_loss(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-leadership-drag-calculator")
def run_leadership_drag_calculator(data: LeadershipDragCalculatorRequest):
    try:
        return calculate_leadership_drag_loss(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-productivity-snapshot")
def run_productivity_snapshot(data: ProductivityInput):
    try:
        return calculate_productivity_metrics(data)
    except Exception as e:
        return {"error": str(e)}


@app.get("/get-industry-benchmarks")
def get_industry_benchmarks(industry: str):
    try:
        b = industry_benchmarks(industry)
        result = {
            "churn_rate": b.get("Employee Churn Rate (%) (Value)", None),
            "inefficiency_rate": b.get("Process Inefficiency Rate (%) (Value)", None),
            "leadership_drag": b.get("Leadership Drag Impact (%) (Value)", None),
            "target_hours_per_employee": b.get("Target Hours per Employee (Value)", None),
            "absenteeism_days": b.get("Absenteeism Days per Month (Value)", None),
            "cac": b.get("Customer Acquisition Cost (CAC) (AUD) (Value)", None)
        }
        return jsonable_encoder(result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
