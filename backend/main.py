from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, confloat
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from admin import admin_router
from calculator import (
    industry_benchmarks,
    calculate_customer_churn_loss,
    calculate_efficiency_loss_and_roi,
    calculate_leadership_drag_loss,
    calculate_productivity_metrics,
    calculate_productivity_metrics_dive
)
from operational_risk import calculate_operational_risk  # ✅ Corrected source
from redis_bridge import store_input, retrieve_input
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


class ProductivityDeepDiveInput(BaseModel):
    industry: str
    total_employees: conint(gt=0)
    avg_salary: confloat(gt=0)
    absenteeism_days: Optional[confloat(ge=0)] = None
    avg_hours: Optional[confloat(ge=0)] = None

# === Calculator Endpoints ===


@app.post("/run-payroll-waste")
def run_payroll_waste_calculator(data: EfficiencyAutoInput):
    try:
        store_input("payroll-waste-inputs", data.dict())
        return calculate_efficiency_loss_and_roi(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-churn-calculator")
def run_churn_calculator(data: ChurnCalculatorRequest):
    try:
        store_input("customer-churn-inputs", data.dict())
        return calculate_customer_churn_loss(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-leadership-drag-calculator")
def run_leadership_drag_calculator(data: LeadershipDragCalculatorRequest):
    try:
        store_input("leadership-drag-inputs", data.dict())
        return calculate_leadership_drag_loss(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-workforce-productivity")
def run_workforce_productivity_calculator(data: ProductivityInput):
    try:
        store_input("workforce-productivity-inputs", data.dict())
        return calculate_productivity_metrics(data)
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-productivity-dive")
def run_productivity_deep_dive(data: ProductivityDeepDiveInput):
    try:
        store_input("productivity-dive-inputs", data.dict())
        return calculate_productivity_metrics_dive(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/run-operational-risk")  # 🚨 NEW
def run_operational_risk_calculator():
    try:
        return calculate_operational_risk()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
