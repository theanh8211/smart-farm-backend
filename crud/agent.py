from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models.agent import Agent

async def get_agent_by_device_id(db: AsyncSession, device_id: str):
    result = await db.execute(select(Agent).where(Agent.device_id == device_id))
    return result.scalar_one_or_none()

async def create_agent(db: AsyncSession, agent_in):
    agent = Agent(**agent_in.dict())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

# Hàm lấy danh sách agents
async def get_agents_list(db: AsyncSession):
    result = await db.execute(
        select(Agent).order_by(Agent.name.asc())  # Sắp xếp tăng dần theo name
        # Nếu muốn sắp xếp giảm dần: .order_by(Agent.name.desc())
    )
    return result.scalars().all()

async def update_agent(db: AsyncSession, agent: Agent, update_data: dict):
    for key, value in update_data.items():
        if value is not None and hasattr(agent, key):
            setattr(agent, key, value)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

async def delete_agent(db: AsyncSession, agent: Agent):
    await db.delete(agent)
    await db.commit()
    return agent

# Hàm cập nhật config (dùng cho PATCH)
async def update_agent_config(db: AsyncSession, agent: Agent, update_data: dict):
    for key, value in update_data.items():
        if value is not None and hasattr(agent, key):
            setattr(agent, key, value)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent
