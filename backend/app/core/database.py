from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/helpdesk.db")

# Create async engine for SQLModel - SQLite doesn't support pool_size and max_overflow
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries - set to False in production
    future=True
)

async def init_db():
    try:
        # Create all tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        # Check if we need to add the is_public column to the ticket table
        async with AsyncSession(engine) as session:
            try:
                # Check if is_public column exists
                result = await session.execute(text("PRAGMA table_info(ticket)"))
                columns = result.fetchall()
                column_names = [column[1] for column in columns]
                
                if "is_public" not in column_names:
                    logger.info("Adding is_public column to ticket table...")
                    # Add the is_public column with a default value of FALSE (0)
                    await session.execute(text("ALTER TABLE ticket ADD COLUMN is_public BOOLEAN DEFAULT 0 NOT NULL"))
                    await session.commit()
                    logger.info("is_public column added successfully!")
                
            except Exception as e:
                logger.error(f"Error checking or adding is_public column: {e}")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

async def get_session() -> AsyncSession:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close() 