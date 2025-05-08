from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from calculator import (
    run_payroll_waste,
    run_customer_churn,
    run_leadership_drag,
    run_workforce_productivity,
    run_productivity_dive,
)

app = FastAPI()

# Enable CORS so frontend (on different domain) can access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Each POST endpoint maps to a calculator module


@app.post("/run-payroll-waste")
def payroll(data: dict):
    return run_payroll_waste(data)


@app.post("/run-customer-churn")
def churn(data: dict):
    return run_customer_churn(data)


@app.post("/run-leadership-drag")
def leadership(data: dict):
    return run_leadership_drag(data)


@app.post("/run-workforce-productivity")
def workforce(data: dict):
    return run_workforce_productivity(data)


@app.post("/run-productivity-dive")
def productivity(data: dict):
    return run_productivity_dive(data)
