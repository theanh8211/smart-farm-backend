from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from core.dependencies import get_db
from models.plant_health import PlantHealth

router = APIRouter()

# Accept both '/api/v1/plant-health' and '/api/v1/plant-health/'
@router.get("")
@router.get("/")
async def get_plant_status(limit: int = 100, status: str = None, db=Depends(get_db)):
    stmt = select(PlantHealth).order_by(PlantHealth.captured_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(PlantHealth.status == status)
    results = (await db.execute(stmt)).scalars().all()
    return results