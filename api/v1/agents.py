from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from core.dependencies import get_db
from schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from crud.agent import create_agent, get_agent_by_device_id, get_agents_list, update_agent, update_agent_config # Thêm get_agents_list
from models.agent import Agent

router = APIRouter(
   # prefix="/agents",
    tags=["agents"])  # Thêm prefix để route là /api/v1/agents

@router.post("/", response_model=AgentResponse)
async def register_agent(agent_in: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = await get_agent_by_device_id(db, agent_in.device_id)
    if agent:
        raise HTTPException(status_code=400, detail="Agent already exists")
    return await create_agent(db, agent_in)

@router.get("/{device_id}/status")
async def agent_status(device_id: str, db: AsyncSession = Depends(get_db)):
    agent = await get_agent_by_device_id(db, device_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"is_online": agent.is_online, "health_score": agent.health_score}

# Endpoint lấy danh sách tất cả agents
@router.get("/", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    return await get_agents_list(db)

# THÊM ENDPOINT PATCH ĐỂ ĐỔI TÊN
@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent_endpoint(
    agent_id: int,
    update_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật thông tin agent (tên, zone, relay overrides, v.v.)"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    return await update_agent(db, agent, update_dict)


@router.patch("/{agent_id}/config", response_model=AgentResponse)
async def update_agent_config_endpoint(
    agent_id: int,
    update_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật các trường cấu hình chuyên biệt của agent (sensor_interval, thresholds, watering_schedule, ...)."""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    return await update_agent_config(db, agent, update_dict)