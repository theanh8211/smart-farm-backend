from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(unique=True, index=True)
    name: str = "Ô đất mới"
    zone: str = "default"
    device_secret: str = Field(exclude=True)
    current_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    is_online: bool = False
    health_score: int = Field(default=100, ge=0, le=100)
    last_seen: Optional[datetime] = None
    firmware_version: str = "1.0.0"
    pump_relay: bool = False
    light_relay: bool = False
    fan_relay: bool = False

    sensor_interval: int = Field(default=4, description="Số lần lấy dữ liệu cảm biến mỗi ngày (1-5)")
    camera_interval: int = Field(default=4, description="Số lần chụp ảnh cho AI mỗi ngày (1-5)")
    humidity_threshold: int = Field(default=40, ge=0, le=100, description="Ngưỡng độ ẩm đất thấp để tưới (%)")
    temperature_threshold: int = Field(default=32, description="Ngưỡng nhiệt độ cao để bật quạt (°C)")
    watering_schedule: Optional[str] = Field(default=None, description="Hẹn giờ tưới cố định, ví dụ: '06:00,18:00'")
    relay_override: bool = Field(default=False, description="Cho phép override relay thủ công")
    deep_sleep_enabled: bool = Field(default=True, description="Chế độ deep sleep để tiết kiệm pin")

    current_ip: Optional[str] = None      
    uptime: Optional[str] = None          
    mac_address: Optional[str] = None