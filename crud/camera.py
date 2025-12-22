from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.camera import Camera

async def create_camera(db: AsyncSession, camera_in):
    camera = Camera(**camera_in.dict())
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    print( "DEBUG: Retrieved cameras from DB" )

    return camera

async def get_cameras_by_agent(db: AsyncSession, agent_id: int):
    result = await db.execute(select(Camera).where(Camera.agent_id == agent_id))
    return result.scalars().all()

async def get_all_cameras(db: AsyncSession):
    result = await db.execute(select(Camera))
    return result.scalars().all()

async def get_camera_by_id(db: AsyncSession, camera_id: int):
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    return result.scalar_one_or_none()

async def update_camera(db: AsyncSession, camera: Camera, update_data: dict):
    for key, value in update_data.items():
        if value is not None and hasattr(camera, key):
            setattr(camera, key, value)
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    return camera

async def delete_camera(db: AsyncSession, camera: Camera):
    await db.delete(camera)
    await db.commit()