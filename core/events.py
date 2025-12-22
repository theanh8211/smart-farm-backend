import logging
from core.logging import logger
from sqlmodel import SQLModel
from core.dependencies import engine


async def startup():
    # Tạo bảng nếu chưa có (tiện cho môi trường dev)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables ensured (create_all).")
    except Exception as e:
        logger.error(f"Error creating DB tables: {e}")

    logger.info("Smart Farm Backend STARTED - Raspberry Pi 5 ready!")


async def shutdown():
    logger.info("Smart Farm Backend SHUTDOWN")