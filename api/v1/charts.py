from fastapi import APIRouter
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/temperature/last-24h")
async def temp_chart():
    now = datetime.utcnow()
    data = []
    for i in range(24):
        ts = now - timedelta(hours=23-i)
        data.append({"time": ts.isoformat(), "value": round(random.uniform(20, 35), 1)})
    return data