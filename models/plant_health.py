from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class PlantHealth(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_id: str
    image_raw: str
    image_processed: Optional[str]
    status: str = "normal"  # normal, weed, pest, unhealthy
    confidence: float
    bbox: str  # JSON string: [[x1,y1,x2,y2], ...]
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None