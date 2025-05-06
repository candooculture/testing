# === operational_risk.py ===

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .redis_logic import retrieve_input

router = APIRouter()

# === INPUT MODEL ===


class DummyInput(BaseModel):
    user_id: str  # Used to namespace keys per user (optional upgrade)

# === RISK SCORE ENDPOINT ===


@router.post("/run-operational-risk")
def run_operational_risk(_: DummyInput):
    try:
        # Keys for stored inputs (assuming one user for now)
        keys = [
            "payroll-waste-inputs",
            "customer-churn-inputs",
            "leadership-drag-inputs",
            "workforce-productivity-inputs",
            "productivity-dive-inputs"
        ]

        inputs = {}
        for key in keys:
            value = retrieve_input(key)
            if value:
                inputs[key] = value

        if not inputs:
            raise HTTPException(
                status_code=400, detail="No module inputs found. Run modules first.")

        # === SAMPLE LOGIC (replace with proper score formula) ===
        # Just tally up presence of modules as a dummy score
        score = len(inputs) * 20
        tier = ("Low" if score <= 40 else "Moderate" if score <= 80 else "High")

        return {
            "formatted_labels": {
                "Operational Risk Score": f"{score}/100",
                "Risk Tier": tier
            },
            "straight_talk": f"Based on completed modules, your operational risk is rated {tier}."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
