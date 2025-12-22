from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smartfarm.db"   # mặc định cho dev
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite") else {}
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
