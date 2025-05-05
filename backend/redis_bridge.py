import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

# === CONFIG ===
REDIS_URL = "https://busy-stud-26783.upstash.io"
REDIS_TOKEN = "AWifAAIjcDEyM2U2NDZjYzU4OWQ0ZDRkOTE3NGFhMTJkMGYxMDc0YnAxMA"
HEADERS = {
    "Authorization": f"Bearer {REDIS_TOKEN}",
    "Content-Type": "application/json"
}

# === SCHEMA ===


class SharedData(BaseModel):
    key: str
    value: dict

# === ROUTES ===


@router.post("/store-shared-data")
async def store_shared_data(payload: SharedData):
    try:
        response = httpx.post(
            f"{REDIS_URL}/set/{payload.key}",
            headers=HEADERS,
            json={"value": payload.value}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Redis set failed")
        return {"message": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-shared-data/{key}")
async def get_shared_data(key: str):
    try:
        response = httpx.get(f"{REDIS_URL}/get/{key}", headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Key not found")
        data = response.json()
        return {"data": data.get("value")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
