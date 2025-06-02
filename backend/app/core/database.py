from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv
import logging
from app.core.config import settings

load_dotenv()

logger = logging.getLogger(__name__)

# Create async engine for SQLModel with PostgreSQL connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Log SQL queries - set to False in production
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE
)

async def init_db():
    try:
        # Create all tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        # Check if we need to add the is_public column to the ticket table
        async with AsyncSession(engine) as session:
            try:
                # Check if is_public column exists using PostgreSQL syntax
                result = await session.execute(
                    text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'ticket' 
                        AND column_name = 'is_public'
                    """)
                )
                column_exists = result.scalar_one_or_none() is not None
                
                if not column_exists:
                    logger.info("Adding is_public column to ticket table...")
                    # Add the is_public column with a default value of FALSE
                    await session.execute(
                        text("ALTER TABLE ticket ADD COLUMN is_public BOOLEAN DEFAULT FALSE NOT NULL")
                    )
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