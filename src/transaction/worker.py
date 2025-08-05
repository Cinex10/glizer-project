import os
from redis import Redis
from rq import Queue, Worker

from logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

# Redis connection configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

def create_redis_connection_for_rq():
    """Create a Redis connection specifically for RQ without decode_responses."""
    try:
        redis_conn = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=False,  # CRITICAL: RQ needs binary data for compression
            socket_connect_timeout=30,
            socket_timeout=30,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test the connection
        redis_conn.ping()
        logger.info(f"Successfully connected RQ Redis at {REDIS_HOST}:{REDIS_PORT}")
        return redis_conn
    except Exception as e:
        logger.error(f"Failed to connect to Redis for RQ: {str(e)}")
        raise

def create_redis_connection_general():
    """Create a Redis connection for general use with decode_responses."""
    try:
        redis_conn = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            encoding='utf-8',
            encoding_errors='replace',
            socket_connect_timeout=30,
            socket_timeout=30,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test the connection
        redis_conn.ping()
        logger.info(f"Successfully connected general Redis at {REDIS_HOST}:{REDIS_PORT}")
        return redis_conn
    except Exception as e:
        logger.error(f"Failed to connect to Redis for general use: {str(e)}")
        raise

# Create Redis connections - separate for RQ and general use
redis_conn_rq = create_redis_connection_for_rq()
redis_conn_general = create_redis_connection_general()

# Create RQ queue with the binary-compatible Redis connection
# Use default Pickle serializer to ensure compatibility between producer and worker
# If you really need JSON serialization, you must upgrade RQ to >=1.15 and pass
# the same serializer object to *both* queue *and* worker at **run time**.
transaction_queue = Queue(
    "transactions",
    connection=redis_conn_rq  # Use binary connection for RQ
)

# Maintenance queue for scheduled jobs (e.g., user-data cleanup)
maintenance_queue = Queue(
    "maintenance",
    connection=redis_conn_rq
)


def get_queue() -> Queue:
    """Get the transaction queue instance."""
    return transaction_queue


def get_redis_connection() -> Redis:
    """Get the general Redis connection instance."""
    return redis_conn_general


def get_redis_connection_rq() -> Redis:
    """Get the RQ-specific Redis connection instance."""
    return redis_conn_rq


def start_worker():
    """Start RQ worker to process transaction jobs."""
    logger.info("Starting RQ worker for transaction processing...")
    try:
        # Use the RQ-specific Redis connection and JSONSerializer
        worker = Worker(
            [transaction_queue, maintenance_queue],
            connection=redis_conn_rq
        )
        logger.info(f"Worker initialized with queues: {transaction_queue.name}, {maintenance_queue.name}")
        # Enable scheduler so that scheduled and repeating jobs are processed
        worker.work(with_scheduler=True)
    except Exception as e:
        logger.error(f"Worker failed: {str(e)}")
        raise


if __name__ == "__main__":
    start_worker() 