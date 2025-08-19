from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Async PostgreSQL connection
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('SQL_USER')}:{os.getenv('SQL_PASSWORD')}"
    f"@postgres:5432/{os.getenv('SQL_DATABASE')}"
)

# For SQLite async (development):
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./notifications.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=True  #
)

AsyncSessionLocal = async_sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine)

Base = declarative_base()