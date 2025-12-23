# backend/api/v1/__init__.py

from .auth import router as auth_router
from .device_auth import router as device_auth_router
from .agents import router as agents_router
from .firmware import router as firmware_router
from .plant_health import router as plant_health_router
from .charts import router as charts_router
from .system import router as system_router
from .saveImg import router as saveImg_router

__all__ = [
    "auth_router",
    "device_auth_router",
    "agents_router",
    "firmware_router",
    "plant_health_router",
    "charts_router",
    "system_router",
    "saveImg_router",
]