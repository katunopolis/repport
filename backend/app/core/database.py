from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/helpdesk.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    }
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session 