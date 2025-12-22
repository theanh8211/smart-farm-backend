from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from datetime import datetime, timedelta

from models.agent import Agent
from core.security import create_access_token
from core.config import settings
from db import get_db

router = APIRouter(prefix="/device", tags=["Device Auth"])


@router.post("/provision")
def provision_device(
    device_id: str,
    device_secret: str,
    db: Session = Depends(get_db)
):
    stmt = select(Agent).where(
        Agent.device_id == device_id,
        Agent.device_secret == device_secret
    )

    agent = db.exec(stmt).one_or_none()

    if not agent:
        raise HTTPException(status_code=401, detail="Invalid device credentials")

    token_exp = timedelta(hours=settings.DEVICE_TOKEN_EXPIRE_HOURS)
    token = create_access_token({"sub": device_id}, token_exp)

    agent.current_token = token
    agent.token_expiry = datetime.utcnow() + token_exp

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "token": token,
        "expires_in_hours": settings.DEVICE_TOKEN_EXPIRE_HOURS
    }


@router.post("/token-refresh")
def refresh_device_token(
    device_id: str,
    current_token: str,
    db: Session = Depends(get_db)
):
    stmt = select(Agent).where(
        Agent.device_id == device_id,
        Agent.current_token == current_token
    )

    agent = db.exec(stmt).one_or_none()

    if not agent:
        raise HTTPException(status_code=401, detail="Invalid token")

    if agent.token_expiry < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")

    token_exp = timedelta(hours=settings.DEVICE_TOKEN_EXPIRE_HOURS)
    new_token = create_access_token({"sub": device_id}, token_exp)

    agent.current_token = new_token
    agent.token_expiry = datetime.utcnow() + token_exp

    db.commit()

    return {"token": new_token}
