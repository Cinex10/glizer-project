# RQ-based Transaction Processing Setup

This project now uses RQ (Redis Queue) for processing transactions with automatic retry functionality.

## Prerequisites

1. **Redis Server**: You need a running Redis server
   ```bash
   # Install Redis (macOS)
   brew install redis
   
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   
   # Start Redis
   redis-server
   ```

2. **Python Dependencies**: Install the updated requirements
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Update your `.env` file with Redis configuration:

```env
# Redis Configuration for RQ
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Transaction Configuration
MAX_RETRIES=3
PERIOD_CHECKING_SECONDS=10
```

## Running the System

### 1. Start the API Server
```bash
python src/main.py
```

### 2. Start RQ Workers
In a separate terminal, start one or more RQ workers:
```bash
python worker.py
```

You can run multiple workers for parallel processing:
```bash
# Terminal 1
python worker.py

# Terminal 2  
python worker.py

# Terminal 3
python worker.py
```

### 3. Monitor Jobs (Optional)
You can use RQ Dashboard to monitor jobs:
```bash
pip install rq-dashboard
rq-dashboard
```

## How It Works

1. **Transaction Creation**: When a transaction is created via `/transaction/create`, it's immediately stored in the database with "pending" status and enqueued as an RQ job.

2. **Job Processing**: RQ workers pick up jobs from the queue and process them. If a job fails, RQ automatically retries it based on the `MAX_RETRIES` configuration.

3. **Retry Logic**: RQ handles retries automatically. After all retries are exhausted, the `on_job_failure` callback is triggered, which marks the transaction as "error" and notifies external systems.

4. **Pending Transaction Recovery**: The API server periodically checks for pending transactions and re-enqueues them as jobs (useful for recovery after system restarts).

## Troubleshooting

### Unicode Decode Error
If you encounter a `UnicodeDecodeError` when starting the worker:
```bash
redis-cli FLUSHALL
```
This clears any corrupted job data from Redis. The system uses JSON serialization to prevent encoding issues.

## Key Benefits

- **Automatic Retries**: RQ handles retry logic automatically
- **Scalability**: Multiple workers can process jobs in parallel
- **Reliability**: Jobs are persisted in Redis and survive system restarts
- **Monitoring**: Built-in job monitoring and failure handling
- **Separation of Concerns**: API server and job processing are decoupled

## Environment Variables

- `MAX_RETRIES`: Maximum number of retry attempts for failed jobs (default: 3)
- `PERIOD_CHECKING_SECONDS`: How often to check for pending transactions (default: 10)
- `REDIS_HOST`: Redis server hostname (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_PASSWORD`: Redis password (optional) 