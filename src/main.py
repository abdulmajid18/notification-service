from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api import endpoints
from src.config.database import engine, Base
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Managed application lifecycle"""
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

    yield

    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed")

app = FastAPI(
    title="Notification Service",
    description="Handles user notifications with Kafka and Redis",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(endpoints.router)

if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        workers=int(os.getenv("WORKERS", "1")),
        log_level=os.getenv("LOG_LEVEL", "info"),
        timeout_keep_alive=int(os.getenv("KEEP_ALIVE", "60")
       ))