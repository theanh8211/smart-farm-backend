from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Firmware(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(unique=True)
    filename: str
    size: int
    changelog: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    ota_success_rate: float = 0.0