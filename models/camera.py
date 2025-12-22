from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class Camera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    rtsp_url: str | None = None
    zone: str | None = None
    is_active: bool = True
    last_snapshot: datetime | None = None
    last_capture: datetime | None = None  
    capture_interval: int | None = None
