from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat
from fastapi.middleware.cors import CORSMiddleware
from admin import admin_router
from calculator import (
    industry_benchmarks,
    calculate_customer_churn_loss,
    calculate_efficiency_loss_and_roi,
    calculate_leadership_drag_loss,
    calculate_productivity_metrics
)
import pandas as pd

app = FastAPI()

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jamescandoo.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Admin Router ===
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

# === Calculator Endpoints ===


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

# === GET Industry Benchmarks for Frontend Pre-Fill ===


@app.get("/get-industry-benchmarks")
def get_industry_benchmarks(industry: str):
    try:
        b = industry_benchmarks(industry)
        return {
            "churn_rate": int(b.get("Customer Churn Rate (%) (Value)", 0)),
            "inefficiency_rate": int(b.get("Process Inefficiency Rate (%) (Value)", 0)),
            "leadership_drag": int(b.get("Leadership Drag Impact (%) (Value)", 10)),
            "target_hours_per_employee": int(b.get("Target Hours per Employee (Value)", 160)),
            "absenteeism_days": float(b.get("Absenteeism Days per Month (Value)", 1.0)),
            "cac": int(b.get("Customer Acquisition Cost (CAC) (AUD) (Value)", 800))
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# === GET Alphabetised Industry List ===


@app.get("/get-all-industries")
def get_all_industries():
    try:
        df = pd.read_csv(
            "benchmarks/final_cleaned_benchmarks_with_certainty.csv")
        industries = sorted(df["Industry"].dropna().unique().tolist())
        return {"industries": industries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
