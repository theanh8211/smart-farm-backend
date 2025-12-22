from pydantic import BaseModel
from typing import Optional

class CameraCreate(BaseModel):
    name: Optional[str] = "Camera mới"
    rtsp_url: str
    agent_id: Optional[int] = None


class CameraResponse(BaseModel):
    id: int
    name: str
    rtsp_url: Optional[str] = None
    agent_id: Optional[int] = None
    stream_url: Optional[str] = None
    is_active: bool
    last_capture: Optional[str]

    class Config:
        from_attributes = True
        orm_mode = True

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    is_active: Optional[bool] = None
    capture_interval: Optional[int] = None
    zone: Optional[str] = None
#    last_snapshot: Optional[str] = None
    agent_id: Optional[int] = None
    stream_url: Optional[str] = None