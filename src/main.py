import os
from fastapi import FastAPI
import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from transaction.routes import router as transaction_router
from transaction.service import resume_pending_transactions

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# async def periodic_transaction_checker():
#     period_checking_seconds = int(os.getenv("PERIOD_CHECKING_SECONDS", 10))
    
#     """Periodically check for pending transactions and resume them."""
#     while True:
#         try:
#             logger.info("Checking for pending transactions to resume...")
#             resume_pending_transactions()
#         except Exception as e:
#             logger.error(f"Error in periodic transaction checker: {str(e)}")
        
#         # Wait for configured period before checking again
#         await asyncio.sleep(period_checking_seconds)


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