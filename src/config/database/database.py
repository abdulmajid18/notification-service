from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL connection (Docker)
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.getenv('SQL_USER')}:{os.getenv('SQL_PASSWORD')}"
    f"@postgres:5432/{os.getenv('SQL_DATABASE')}"
)

# SQLite fallback for development
# SQLALCHEMY_DATABASE_URL = "sqlite:///./notifications.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()