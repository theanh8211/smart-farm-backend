import logging
from core.logging import logger
from sqlmodel import SQLModel
from core.dependencies import engine
from core.dependencies import async_session

# On startup, start HLS workers for cameras marked active in DB
from crud.camera import get_all_cameras
from api.v1.cameras import camera_processes
from services.ffmpeg_stream import start_supervised_hls


async def startup():
    # Tạo bảng nếu chưa có (tiện cho môi trường dev)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables ensured (create_all).")
    except Exception as e:
        logger.error(f"Error creating DB tables: {e}")

    logger.info("Smart Farm Backend STARTED - Raspberry Pi 5 ready!")
    # Start HLS ffmpeg processes for any cameras that are active in DB
    try:
        async with async_session() as session:
            cameras = await get_all_cameras(session)
            for cam in cameras:
                if getattr(cam, 'is_active', False):
                    # start supervised ffmpeg HLS so it will be restarted on failure
                    ctrl = start_supervised_hls(cam.id, cam.rtsp_url)
                    if ctrl is not None:
                        camera_processes[cam.id] = ctrl
    except Exception as e:
        logger.error(f"Error starting camera HLS processes on startup: {e}")


async def shutdown():
    logger.info("Smart Farm Backend SHUTDOWN")