from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RiskInput(BaseModel):
    # Payroll Module
    payroll_cost: float = 0
    avg_salary: float = 0
    improvement_rate: float = 0

    # Churn Module
    churn_rate: float = 0
    desired_improvement: float = 0
    cac: float = 0
    avg_revenue: float = 0
    num_customers: int = 0

    # Leadership Module
    leadership_drag: float = 0

    # Workforce Productivity
    total_revenue: float = 0
    productive_hours: float = 0
    target_hours_per_employee: float = 0
    overtime_hours: float = 0

    # Deep Dive
    absenteeism_days: float = 0
    avg_hours: float = 0

    # Shared
    total_employees: int = 0
    industry: str = ""


@router.post("/run-operational-risk")
def run_operational_risk(data: RiskInput):
    try:
        inputs = data.dict()
        print("🔍 ORS Received Payload:", inputs)

        module_checks = {
            "Payroll": inputs.get("payroll_cost", 0) > 0,
            "Churn": inputs.get("churn_rate", 0) > 0,
            "Leadership": inputs.get("leadership_drag", 0) > 0,
            "Productivity": inputs.get("productive_hours", 0) > 0,
            "Deep Dive": inputs.get("avg_salary", 0) > 0 and inputs.get("absenteeism_days", 0) > 0
        }

        completed_modules = [name for name, passed in module_checks.items() if passed]
        num_modules = len(completed_modules)

        if num_modules == 0:
            raise HTTPException(
                status_code=400,
                detail=f"No valid modules detected. Payload: {inputs}"
            )

        score = num_modules * 20
        tier = "Low" if score <= 40 else "Moderate" if score <= 80 else "High"

        return {
            "formatted_labels": {
                "Operational Risk Score": f"{score}/100",
                "Risk Tier": tier
            },
            "straight_talk": f"✅ Completed Modules: {', '.join(completed_modules)}\n❌ Blind Spots: {5 - num_modules} module(s) unaccounted for.\n\nThis score highlights where risk is hidden and resilience is weak."
        }

    except Exception as e:
        print("🔥 ORS Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
