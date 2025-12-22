from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    zone: str = "default"

class AgentCreate(AgentBase):
    device_id: str
    device_secret: str
    name: Optional[str] = "Thiết bị mới"
    zone: Optional[str] = "default"      

class AgentResponse(AgentBase):
    id: int
    device_id: str
    is_online: bool
    health_score: int
    last_seen: Optional[datetime]
    firmware_version: str

    class Config:
        from_attributes = True

# THÊM SCHEMA CHO CẬP NHẬT
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    sensor_interval: Optional[int] = None
    camera_interval: Optional[int] = None
    humidity_threshold: Optional[int] = None
    temperature_threshold: Optional[int] = None
    watering_schedule: Optional[str] = None
    relay_override: Optional[bool] = None
    deep_sleep_enabled: Optional[bool] = None
    pump_relay: Optional[bool] = None
    light_relay: Optional[bool] = None
    fan_relay: Optional[bool] = None

class AgentResponse(AgentBase):
    id: int
    device_id: str
    is_online: bool
    health_score: int
    last_seen: Optional[datetime]
    firmware_version: str
    sensor_interval: int
    camera_interval: int
    humidity_threshold: int
    temperature_threshold: int
    watering_schedule: Optional[str]
    relay_override: bool
    deep_sleep_enabled: bool
    pump_relay: Optional[bool] = None
    light_relay: Optional[bool] = None
    fan_relay: Optional[bool] = None
    class Config:
        from_attributes = True