from fastapi import FastAPI
import uvicorn
from logging_config import get_logger
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from datetime import timedelta
from rq import Queue, Repeat
from transaction.worker import get_redis_connection_rq
from cleanup import delete_user_data_folder

from transaction.routes import router as transaction_router

load_dotenv()

# Setup centralized logging
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting up - checking for pending transactions...")
    
    try:
        # resume_pending_transactions()
        logger.info("Startup transaction resume completed")
    except Exception as e:
        logger.error(f"Error during startup transaction resume: {str(e)}")

    # ------------------------------------------------------------------
    # Schedule periodic cleanup of user-data folder using RQ
    # ------------------------------------------------------------------
    try:
        ttl_days = int(os.getenv("USER_DATA_TTL_IN_DAYS", "3"))
        interval_seconds = int(timedelta(days=ttl_days).total_seconds())  # convert days to seconds

        maintenance_queue = Queue(
            "maintenance",
            connection=get_redis_connection_rq()
        )

        maintenance_queue.enqueue(
            delete_user_data_folder,
            job_id="cleanup_user_data_folder",
            repeat=Repeat(times=1000000, interval=60)
        )

        logger.info(f"Scheduled cleanup job for 'user-data' folder every {ttl_days} days")
    except Exception as e:
        logger.error(f"Failed to schedule 'user-data' cleanup job: {str(e)}")
    
    # Start the periodic checker
    # checker_task = asyncio.create_task(periodic_transaction_checker())
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    # checker_task.cancel()
    # try:
    #     await checker_task
    # except asyncio.CancelledError:
    #     pass


app = FastAPI(lifespan=lifespan)

app.include_router(transaction_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)