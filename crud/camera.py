from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.camera import Camera
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, DBAPIError

async def create_camera(db: AsyncSession, camera_in):
    camera = Camera(**camera_in.dict())
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    print( "DEBUG: Retrieved cameras from DB" )

    return camera

async def get_cameras_by_agent(db: AsyncSession, agent_id: int):
    try:
        result = await db.execute(select(Camera).where(Camera.agent_id == agent_id))
        return result.scalars().all()
    except (ProgrammingError, DBAPIError) as e:
        # Fallback for missing columns (e.g., stream_url not present in DB)
        # If the session/transaction is in a failed state, rollback first.
        try:
            await db.rollback()
        except Exception:
            pass
        msg = str(e)
        if 'stream_url' in msg or 'UndefinedColumnError' in msg:
            stmt = text(
                "SELECT id,name,rtsp_url,agent_id,zone,is_active,last_snapshot,last_capture,capture_interval FROM camera WHERE agent_id = :agent_id"
            )
            result = await db.execute(stmt, {"agent_id": agent_id})
            rows = result.all()
            cameras = []
            for r in rows:
                data = dict(r._mapping) if hasattr(r, '_mapping') else dict(r)
                data['stream_url'] = None
                cameras.append(Camera(**data))
            return cameras
        raise

async def get_all_cameras(db: AsyncSession):
    try:
        result = await db.execute(select(Camera))
        return result.scalars().all()
    except (ProgrammingError, DBAPIError) as e:
        # Fallback when a column from model isn't in DB yet (typical during missing migration)
        # Ensure we rollback failed transaction before running fallback SELECT.
        try:
            await db.rollback()
        except Exception:
            pass
        msg = str(e)
        if 'stream_url' in msg or 'UndefinedColumnError' in msg:
            stmt = text(
                "SELECT id,name,rtsp_url,agent_id,zone,is_active,last_snapshot,last_capture,capture_interval FROM camera"
            )
            result = await db.execute(stmt)
            rows = result.all()
            cameras = []
            for r in rows:
                data = dict(r._mapping) if hasattr(r, '_mapping') else dict(r)
                data['stream_url'] = None
                cameras.append(Camera(**data))
            return cameras
        raise

async def get_camera_by_id(db: AsyncSession, camera_id: int):
    try:
        result = await db.execute(select(Camera).where(Camera.id == camera_id))
        return result.scalar_one_or_none()
    except (ProgrammingError, DBAPIError) as e:
        try:
            await db.rollback()
        except Exception:
            pass
        msg = str(e)
        if 'stream_url' in msg or 'UndefinedColumnError' in msg:
            stmt = text(
                "SELECT id,name,rtsp_url,agent_id,zone,is_active,last_snapshot,last_capture,capture_interval FROM camera WHERE id = :id"
            )
            result = await db.execute(stmt, {"id": camera_id})
            row = result.first()
            if not row:
                return None
            data = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
            data['stream_url'] = None
            return Camera(**data)
        raise

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