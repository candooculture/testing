from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conint, confloat
from calculator import (
    industry_benchmarks,
    calculate_efficiency_loss_and_roi,
    calculate_customer_churn_loss,
    calculate_leadership_drag_loss,
    calculate_productivity_metrics,
    get_industry_benchmarks as get_full_benchmark_data
)

app = FastAPI()

# Allow frontend (adjust domain in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === INPUT MODELS ===


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

# === ENDPOINTS ===


@app.post("/run-efficiency-calculator")
def run_efficiency_calculator(data: EfficiencyAutoInput):
    return calculate_efficiency_loss_and_roi(data)


@app.post("/run-churn-calculator")
def run_churn_calculator(data: ChurnCalculatorRequest):
    return calculate_customer_churn_loss(data)


@app.post("/run-leadership-drag-calculator")
def run_leadership_drag_calculator(data: LeadershipDragCalculatorRequest):
    return calculate_leadership_drag_loss(data)


@app.post("/run-productivity-snapshot")
def run_productivity_snapshot(data: ProductivityInput):
    return calculate_productivity_metrics(data)


@app.get("/get-industry-benchmarks")
def get_industry_benchmarks(industry: str):
    try:
        b = industry_benchmarks(industry)
        return {
            "churn_rate": b.get("Employee Churn Rate (%) (Value)", None),
            "inefficiency_rate": b.get("Process Inefficiency Rate (%) (Value)", None),
            "leadership_drag": b.get("Leadership Drag Impact (%) (Value)", None),
            "target_hours_per_employee": b.get("Target Hours per Employee (Value)", None),
            "absenteeism_days": b.get("Absenteeism Days per Month (Value)", None),
            "cac": b.get("Customer Acquisition Cost (CAC) (AUD) (Value)", None)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
