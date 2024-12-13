from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
#import os

#file_path = os.path.join("Users", "kaifq", "OneDrive", "Desktop", "case and user management", "usermanagement", "db.sqlite3")

#abs_path = os.path.abspath(file_path)

DATABASE_URL = "sqlite+aiosqlite:///C:/Users/kaifq/OneDrive/Desktop/case and user management/usermanagement/db.sqlite3"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


async def get_db()->AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
       await db.close()
