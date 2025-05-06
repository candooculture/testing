from fastapi import HTTPException
from pydantic import BaseModel
from redis_bridge import retrieve_input  # ✅ Correct import

# === INPUT MODEL ===


class DummyInput(BaseModel):
    user_id: str  # For future use, not currently implemented

# === RISK SCORE ENDPOINT ===


def calculate_operational_risk():
    try:
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

        # === SAMPLE LOGIC ===
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
