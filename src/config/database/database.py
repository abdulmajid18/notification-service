from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# For SQLite sync (development):
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./data/notifications.db')

# Create sync engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Important for SQLite
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=True
)

# Create sync session maker
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()