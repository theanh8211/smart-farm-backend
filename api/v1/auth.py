from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import create_access_token, verify_password
from models.user import User

router = APIRouter()

@router.post("/login")
async def login(username: str, password: str):
    # Tìm user, check password, trả JWT
    async with AsyncSession() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")
        token = create_access_token({"sub": username})
        return {"access_token": token}
        