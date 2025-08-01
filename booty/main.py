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

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(admin_router)

# === Input Models ===

class EfficiencyAutoInput(BaseModel):
    industry: str
    total_employees: int
    avg_salary: float
    improvement_rate: float

class ChurnCalculatorRequest(BaseModel):
    num_customers: int
    churn_rate: float
    avg_revenue: float
    cac: float
    desired_improvement: float
    industry: str

class LeadershipDragCalculatorRequest(BaseModel):
    industry: str
    total_employees: int
    avg_salary: float
    leadership_drag: float

class WorkforceProductivityFullRequest(BaseModel):
    industry: str
    total_revenue: float
    payroll_cost: float
    total_employees: int
    productive_hours: float
    target_hours_per_employee: float
    absenteeism_days: float
    overtime_hours: float

class ProductivityDeepDiveInput(BaseModel):
    industry: str
    total_employees: int
    avg_salary: float
    absenteeism_days: Optional[float] = 0
    avg_hours: Optional[float] = 0

# === Module Calculators ===

@app.post("/run-payroll-waste")
def run_payroll_waste(data: EfficiencyAutoInput):
    return calculate_efficiency_loss_and_roi(data)

@app.post("/run-churn-calculator")
def run_churn(data: ChurnCalculatorRequest):
    return calculate_customer_churn_loss(data)

@app.post("/run-leadership-drag-calculator")
def run_leadership_drag(data: LeadershipDragCalculatorRequest):
    return calculate_leadership_drag_loss(data)

@app.post("/run-workforce-productivity")
def run_workforce_productivity(data: WorkforceProductivityFullRequest):
    return calculate_productivity_metrics(data)

@app.post("/run-productivity-dive")
def run_productivity_dive(data: ProductivityDeepDiveInput):
    return calculate_productivity_metrics_dive(data)

@app.get("/get-industry-benchmarks")
def get_industry_benchmarks(industry: str):
    b = industry_benchmarks(industry)
    return {
        "churn_rate": int(b.get("Customer Churn Rate (%) (Value)", 0)),
        "inefficiency_rate": int(b.get("Process Inefficiency Rate (%) (Value)", 0)),
        "leadership_drag": int(b.get("Leadership Drag Impact (%) (Value)", 10)),
        "target_hours_per_employee": int(b.get("Target Hours per Employee (Value)", 160)),
        "absenteeism_days": float(b.get("Absenteeism Days per Month (Value)", 1.0)),
        "cac": int(b.get("Customer Acquisition Cost (CAC) (AUD) (Value)", 800))
    }

@app.get("/get-all-industries")
def get_all_industries():
    df = pd.read_csv("benchmarks/final_cleaned_benchmarks_with_certainty.csv")
    return {"industries": sorted(df["Industry"].dropna().unique().tolist())}

# === ORS Scoring Endpoint ===

@app.post("/run-operational-risk")
def run_operational_risk_calculator(data: RiskInput):
    try:
        return run_operational_risk(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Email Report Builder ===

def format_dollars(value):
    if value is None or value == "N/A":
        return "$N/A"
    try:
        return f"${float(value):,.0f}"
    except:
        return "$N/A"

def render_report_html(data):
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>ORS Report</title></head>
    <body style='font-family: Arial, sans-serif; max-width: 640px; margin: 0 auto; padding: 20px; color: #eee; background-color: #1a1a1a;'>
      <h2 style='text-align: center;'>📊 Operational Risk Summary</h2>
      <p style='text-align: center; color: #ccc;'>Snapshot of your financial risk due to operational inefficiencies.</p>
      <hr style='margin: 20px 0; border: none; border-top: 1px solid #444;' />

      <h3>🔥 EBITDA at Risk</h3>
      <ul>
        <li><strong>Total Risk Impact:</strong> {format_dollars(data.get("total_risk_dollars"))}</li>
        <li><strong>Estimated EBITDA Margin:</strong> {data.get("ebitda_margin", "N/A")}%</li>
        <li><strong>EBITDA at Risk:</strong> {data.get("ebitda_risk_pct", "N/A")}%</li>
      </ul>

      <h3>📋 Risk Breakdown</h3>
      <ul>
        <li>Payroll Waste: {format_dollars(data.get("module_breakdown", {}).get("Payroll Waste"))}</li>
        <li>Customer Churn: {format_dollars(data.get("module_breakdown", {}).get("Customer Churn"))}</li>
        <li>Leadership Drag: {format_dollars(data.get("module_breakdown", {}).get("Leadership Drag"))}</li>
        <li>Workforce Productivity: {format_dollars(data.get("module_breakdown", {}).get("Workforce Productivity"))}</li>
        <li>Process Gaps: {format_dollars(data.get("module_breakdown", {}).get("Process Gaps (Deep Dive)"))}</li>
      </ul>

      <h3>🧠 Inputs Summary</h3>
    <p style='color: #999; font-size: 13px;'><em>Note: Fields marked as “benchmark” were auto-filled based on your selected industry.</em></p>
    <ul>
      <!-- Business Context -->
      <li><strong>Industry:</strong> {data.get("industry", "N/A")} <em>(selected)</em></li>
      <li><strong>Total Employees:</strong> {data.get("total_employees", "N/A")} <em>(user-entered)</em></li>
      <li><strong>Average Salary:</strong> {format_dollars(data.get("avg_salary"))} <em>(user-entered)</em></li>
      <li><strong>Total Revenue:</strong> {format_dollars(data.get("total_revenue"))} <em>(user-entered)</em></li>
    
      <!-- Customer Economics -->
      <li><strong>Number of Customers:</strong> {data.get("num_customers", "N/A")} <em>(user-entered)</em></li>
      <li><strong>Average Revenue per Customer:</strong> {format_dollars(data.get("avg_revenue"))} <em>(user-entered)</em></li>
      <li><strong>CAC:</strong> {format_dollars(data.get("cac"))} <em>(user-entered)</em></li>
      <li><strong>Churn Rate:</strong> {data.get("churn_rate", "N/A")}% <em>(user-entered)</em></li>
      <li><strong>Desired Improvement:</strong> {data.get("desired_improvement", "N/A")}% <em>(user-entered)</em></li>
    
      <!-- Leadership & Productivity -->
      <li><strong>Leadership Drag:</strong> {data.get("leadership_drag", "N/A")}% <em>(user-entered)</em></li>
      <li><strong>Improvement Rate:</strong> {data.get("improvement_rate", "N/A")}% <em>(user-entered)</em></li>
      <li><strong>Productive Hours:</strong> {data.get("productive_hours", "N/A")} <em>(user-entered)</em></li>
      <li><strong>Target Hours per Employee:</strong> {data.get("target_hours_per_employee", "N/A")} <em>(benchmark)</em></li>
      <li><strong>Average Weekly Hours:</strong> {data.get("avg_hours", "N/A")} <em>(user-entered)</em></li>
      <li><strong>Overtime Hours:</strong> {data.get("overtime_hours", "N/A")} <em>(user-entered)</em></li>
      <li><strong>Absenteeism Days:</strong> {data.get("absenteeism_days", "N/A")} <em>(user-entered)</em></li>
    
      <!-- Calculated -->
      <li><strong>Payroll Cost:</strong> {format_dollars(data.get("payroll_cost"))} <em>(calculated)</em></li>
    </ul>


      <p style='margin-top: 30px; font-size: 14px; color: #777;'>Generated by the Candoo Culture ORS Engine.</p>
    </body>
    </html>
    """

@app.post("/send-risk-report")
async def send_risk_report(request: Request):
    try:
        data = await request.json()

        # === Run ORS Calculation and inject results ===
        try:
            ors_result = run_operational_risk(RiskInput(**data))
            data.update(ors_result)
        except Exception as calc_error:
            print("ORS calculation failed:", calc_error)

        # === Mailgun ===
        mg_api_key = os.getenv("MAILGUN_API_KEY")
        mg_domain = os.getenv("MAILGUN_DOMAIN")
        mg_sender = os.getenv("MAILGUN_SENDER")

        if not all([mg_api_key, mg_domain, mg_sender]):
            raise Exception("Missing Mailgun environment variables.")

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
        raise HTTPException(status_code=500, detail=str(e))
