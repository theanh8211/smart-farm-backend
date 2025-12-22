import os
from fastapi import HTTPException
from models.agent import Agent
from sqlmodel.ext.asyncio.session import AsyncSession

FIRMWARE_DIR = "/app/firmware"

async def get_latest_firmware_version() -> str:
    files = [f for f in os.listdir(FIRMWARE_DIR) if f.endswith(".bin")]
    if not files:
        raise HTTPException(404, "No firmware available")
    # Giả sử tên file là version.bin → 1.2.3.bin
    versions = sorted(files, key=lambda x: x.split(".")[0], reverse=True)
    return versions[0].replace(".bin", "")

async def trigger_ota_for_agent(agent: Agent, db: AsyncSession):
    latest_ver = await get_latest_firmware_version()
    if agent.firmware_version == latest_ver:
        return {"status": "already latest"}
    
    # Ở đây sẽ gửi lệnh OTA qua MQTT hoặc WebSocket
    # Hiện tại chỉ cập nhật DB để ESP32 polling thấy
    agent.firmware_version = latest_ver
    agent.ota_pending = True
    await db.commit()
    return {"status": "ota_triggered", "new_version": latest_ver}