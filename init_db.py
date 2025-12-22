from sqlmodel import SQLModel
from db import engine
import models  # import để SQLModel biết các bảng

def init_db():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
