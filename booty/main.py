from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from admin import admin_router
from calculator import (
    industry_benchmarks,
    calculate_customer_churn_loss,
    calculate_efficiency_loss_and_roi,
    calculate_leadership_drag_loss,
    calculate_productivity_metrics,
    calculate_productivity_metrics_dive,
)
from operational_risk import run_operational_risk, RiskInput
import pandas as pd
import os
import requests

app = FastAPI()

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# === Admin Router ===
app.include_router(admin_router)

# === Input Models ===

class EfficiencyAutoInput(BaseModel):
    industry: str
    total_employees: int = Field(..., gt=0)
    avg_salary: float = Field(..., gt=0)
    improvement_rate: float = Field(..., gt=0, lt=100)

class ChurnCalculatorRequest(BaseModel):
    num_customers: int = Field(..., gt=0)
    churn_rate: float = Field(..., gt=0, lt=100)
    avg_revenue: float = Field(..., gt=0)
    cac: float = Field(..., ge=0)
    desired_improvement: float = Field(..., gt=0, lt=100)
    industry: str

class WorkforceProductivityRequest(BaseModel):
    industry: str
    total_employees: int = Field(..., gt=0)
    avg_salary: float = Field(..., gt=0)
    productivity_loss: float = Field(..., gt=0, lt=100)

class LeadershipDragCalculatorRequest(BaseModel):
    industry: str
    total_employees: int = Field(..., gt=0)
    avg_salary: float = Field(..., gt=0)
    leadership_drag: float = Field(..., gt=0, lt=100)

class WorkforceProductivityFullRequest(BaseModel):
    industry: str
    total_revenue: float = Field(..., gt=0)
    payroll_cost: float = Field(..., gt=0)
    total_employees: int = Field(..., gt=0)
    productive_hours: float = Field(..., gt=0)
    target_hours_per_employee: float = Field(..., gt=0)
    absenteeism_days: float = Field(..., ge=0)
    overtime_hours: float = Field(..., ge=0)

class ProductivityDeepDiveInput(BaseModel):
    industry: str
    total_employees: int = Field(..., gt=0)
    avg_salary: float = Field(..., gt=0)
    absenteeism_days: Optional[float] = Field(None, ge=0)
    avg_hours: Optional[float] = Field(None, ge=0)

# === Calculator Endpoints ===

@app.post("/run-payroll-waste")
def run_payroll_waste_calculator(data: EfficiencyAutoInput):
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

@app.post("/run-workforce-productivity")
def run_workforce_productivity(data: WorkforceProductivityFullRequest):
    try:
        result = calculate_productivity_metrics(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-productivity-dive")
def run_productivity_deep_dive(data: ProductivityDeepDiveInput):
    try:
        return calculate_productivity_metrics_dive(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/run-operational-risk")
def run_operational_risk_calculator(data: RiskInput):
    try:
        return run_operational_risk(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/get-all-industries")
def get_all_industries():
    try:
        df = pd.read_csv("benchmarks/final_cleaned_benchmarks_with_certainty.csv")
        industries = sorted(df["Industry"].dropna().unique().tolist())
        return {"industries": industries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === HTML Report Generator ===

def render_report_html(data):
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>ORS Report</title></head>
    <body style='font-family: Arial, sans-serif; max-width: 640px; margin: 0 auto; padding: 20px; color: #333;'>
      <h2 style='text-align: center;'>📊 Operational Risk Summary</h2>
      <p style='text-align: center; color: #555;'>Snapshot of inefficiencies based on your inputs.</p>
      <hr style='margin: 20px 0; border: none; border-top: 1px solid #eee;' />
      
      <h3>💰 Payroll Waste</h3>
      <ul>
        <li><strong>Employees:</strong> {data.get("total_employees", "N/A")}</li>
        <li><strong>Average Salary:</strong> ${data.get("avg_salary", "N/A")}</li>
        <li><strong>Inefficiency:</strong> {data.get("improvement_rate", "N/A")}%</li>
      </ul>

      <h3>📉 Customer Churn</h3>
      <ul>
        <li><strong>Churn Rate:</strong> {data.get("churn_rate", "N/A")}%</li>
        <li><strong>Revenue/Customer:</strong> ${data.get("avg_revenue", "N/A")}</li>
        <li><strong>CAC:</strong> ${data.get("cac", "N/A")}</li>
      </ul>

      <h3>🧠 Leadership Drag</h3>
      <ul>
        <li><strong>Leadership Drag:</strong> {data.get("leadership_drag", "N/A")}%</li>
      </ul>

      <h3>⚙️ Workforce Productivity</h3>
      <ul>
        <li><strong>Productive Hours:</strong> {data.get("productive_hours", "N/A")}</li>
        <li><strong>Target Hours:</strong> {data.get("target_hours_per_employee", "N/A")}</li>
        <li><strong>Overtime:</strong> {data.get("overtime_hours", "N/A")}</li>
      </ul>

      <h3>🏥 Productivity Deep Dive</h3>
      <ul>
        <li><strong>Absenteeism Days:</strong> {data.get("absenteeism_days", "N/A")}</li>
        <li><strong>Average Weekly Hours:</strong> {data.get("avg_hours", "N/A")}</li>
      </ul>

      <p style='margin-top: 30px; font-size: 14px; color: #777;'>Generated by the Candoo Culture ORS Engine.</p>
    </body>
    </html>
    """

# === Report Sender ===

@app.post("/send-risk-report")
async def send_risk_report(request: Request):
    try:
        data = await request.json()
        print("📨 Sending Risk Report:", data)

        mg_api_key = os.getenv("MAILGUN_API_KEY")
        mg_domain = os.getenv("MAILGUN_DOMAIN")
        mg_sender = os.getenv("MAILGUN_SENDER")

        if not all([mg_api_key, mg_domain, mg_sender]):
            raise Exception("Missing one or more Mailgun environment variables.")

        response = requests.post(
            f"https://api.mailgun.net/v3/{mg_domain}/messages",
            auth=("api", mg_api_key),
            data={
                "from": f"Candoo Culture Reports <{mg_sender}>",
                "to": [data["recipient"]],
                "subject": data["subject"],
                "html": render_report_html(data)
            }
        )

        if response.status_code != 200:
            raise Exception(f"Mailgun Error: {response.text}")

        return {"success": True, "message": "Report sent."}

    except Exception as e:
        print("❌ Report Sending Failed:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
