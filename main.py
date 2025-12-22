from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core import events, config, logging
from fastapi.staticfiles import StaticFiles

# Import router
from api.v1 import auth, device_auth, agents, firmware, plant_health, charts, system
from api.v1.cameras import router as cameras_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await events.startup()
    yield
    await events.shutdown()

app = FastAPI(
    title="Smart Farm Web v1.0",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],  # Thêm origin frontend chính xác
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

# Mount HLS directory
os.makedirs("hls", exist_ok=True)
app.mount("/hls", StaticFiles(directory="hls"), name="hls")

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(device_auth.router, prefix="/api/v1/device", tags=["device"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(firmware.router, prefix="/api/v1/firmware", tags=["firmware"])
app.include_router(cameras_router, prefix="/api/v1/cameras", tags=["cameras"])
app.include_router(plant_health.router, prefix="/api/v1/plant-health", tags=["plant-health"])
app.include_router(charts.router, prefix="/api/v1/charts", tags=["charts"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])

@app.get("/")
async def root():
    return {"message": "Smart Farm Web v1.0 - Running on Raspberry Pi 5"}