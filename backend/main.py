from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculator import (
    run_payroll_waste,
    run_customer_churn,
    run_leadership_drag,
    run_workforce_productivity,
    run_productivity_dive,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can tighten this later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run-payroll-waste")
async def payroll(request: Request):
    data = await request.json()
    return run_payroll_waste(data)


@app.post("/run-customer-churn")
async def churn(request: Request):
    data = await request.json()
    return run_customer_churn(data)


@app.post("/run-leadership-drag")
async def leadership(request: Request):
    data = await request.json()
    return run_leadership_drag(data)


@app.post("/run-workforce-productivity")
async def workforce(request: Request):
    data = await request.json()
    return run_workforce_productivity(data)


@app.post("/run-productivity-dive")
async def productivity(request: Request):
    data = await request.json()
    return run_productivity_dive(data)
