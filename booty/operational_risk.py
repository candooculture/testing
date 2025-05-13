
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class RiskInput(BaseModel):
    payroll_cost: float = 0
    churn_rate: float = 0
    leadership_drag: float = 0
    total_revenue: float = 0
    avg_salary: float = 0
    productive_hours: float = 0
    total_employees: int = 0
    improvement_rate: float = 0
    desired_improvement: float = 0
    absenteeism_days: float = 0
    productivity_loss: float = 0
    overtime_hours: float = 0


@router.post("/run-operational-risk")
def run_operational_risk(data: RiskInput):
    try:
        inputs = data.dict()
        num_modules = 0

        if inputs.get("payroll_cost", 0) > 0:
            num_modules += 1
        if inputs.get("churn_rate", 0) > 0:
            num_modules += 1
        if inputs.get("leadership_drag", 0) > 0:
            num_modules += 1
        if inputs.get("productive_hours", 0) > 0:
            num_modules += 1
        if inputs.get("avg_salary", 0) > 0 and inputs.get("productivity_loss", 0) > 0:
            num_modules += 1

        if num_modules == 0:
            raise HTTPException(
                status_code=400, detail="No valid inputs received.")

        score = num_modules * 20
        tier = "Low" if score <= 40 else "Moderate" if score <= 80 else "High"

        return {
            "formatted_labels": {
                "Operational Risk Score": f"{score}/100",
                "Risk Tier": tier
            },
            "straight_talk": f"Your organisation shows risk in {5 - num_modules} areas. This score helps highlight blind spots and build resilience."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
