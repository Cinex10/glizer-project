# Yalla Pay Recharge Bot

Automated bot for YallaPay recharges with REST API, Redis Queue background processing, and webhook support.

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone and Setup
```bash
# Clone the project
git clone <your-repo>
cd yalla_ludo

# Copy environment configuration
cp env.example .env
# Edit .env with your actual configuration values
```

### 2. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Services Available
- **API**: http://localhost:8000 - Main FastAPI application
- **Webhook**: http://localhost:8001 - Webhook receiver
- **RQ Dashboard**: http://localhost:9181 - Job monitoring interface
- **Redis**: localhost:6379 - Redis queue backend

## 📦 Docker Services

The Docker setup includes:

- **Redis**: Job queue backend
- **API**: Main FastAPI application with transaction processing
- **Webhook**: Webhook receiver service
- **Worker1 & Worker2**: Background job processors
- **RQ Dashboard**: Web interface for monitoring jobs

### Docker Management Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f worker1

# Scale workers
docker-compose up -d --scale worker1=3 --scale worker2=2

# Rebuild after code changes
docker-compose build

# Remove everything including volumes
docker-compose down -v
```

## 🛠 Manual Installation (Development)

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Install ChromeDriver
# Ubuntu/Debian:
sudo apt install chromium-chromedriver
# or download from https://chromedriver.chromium.org/

# Install and start Redis
# macOS:
brew install redis && redis-server
# Ubuntu/Debian:
sudo apt-get install redis-server && redis-server
```

### Setup Environment
```bash
# Copy environment file
cp env.example .env

# Edit .env with your configuration:
# BOT_TOKEN=your_bot_token
# GLIZER_TOKEN=your_glizer_token
# DATABASE_URL=sqlite:///./transactions.db
# REDIS_HOST=localhost
# REDIS_PORT=6379
# etc.
```

### Start Services Manually
```bash
# Terminal 1: Start the API
python src/main.py

# Terminal 2: Start webhook service
python webhook.py

# Terminal 3: Start RQ worker
python worker.py

# Terminal 4: (Optional) Start RQ Dashboard
pip install rq-dashboard
rq-dashboard
```

## 📁 Project Structure

```
yalla_ludo/
├── src/
│   ├── main.py              # Main FastAPI application
│   ├── database.py          # Database configuration
│   ├── transaction/         # Transaction processing module
│   │   ├── routes.py        # API routes
│   │   ├── service.py       # Business logic
│   │   ├── models.py        # Database models
│   │   ├── worker.py        # RQ worker configuration
│   │   └── utils.py         # Utility functions
│   └── yalla_ludo/          # Yalla Ludo specific logic
├── webhook.py               # Webhook receiver
├── worker.py               # RQ worker startup script
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Container image definition
├── requirements.txt        # Python dependencies
└── env.example             # Environment variables template
```

## 🔧 API Usage

### Transaction Endpoints

**Create Transaction:**
```bash
curl -X POST "http://localhost:8000/transaction/create" \
  -H "Content-Type: application/json" \
  -H "token: YOUR_BOT_TOKEN" \
  -d '{
    "usd_value": "2",
    "choix": "almas",
    "ID": "7915329",
    "pin_code": "3J22NN6P16KA"
  }'
```

**Check Transaction Status:**
```bash
curl "http://localhost:8000/transaction/status/{transaction_id}" \
  -H "token: YOUR_BOT_TOKEN"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## 🔍 Available Endpoints

- `GET /health` - Health check
- `POST /transaction/create` - Create new transaction (requires token)
- `GET /transaction/status/{id}` - Get transaction status (requires token)
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## 📊 Monitoring

### RQ Dashboard
Access the job monitoring interface at http://localhost:9181 to:
- View active, failed, and completed jobs
- Monitor worker status
- Retry failed jobs
- View job details and logs

### Logs
```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f worker1
docker-compose logs -f webhook

# Manual setup logs
# Check application logs in the terminal outputs
```

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Authentication
BOT_TOKEN=your_bot_token_here
GLIZER_TOKEN=your_glizer_token_here

# Database
DATABASE_URL=sqlite:///./data/transactions.db

# Redis Configuration
REDIS_HOST=redis  # or localhost for manual setup
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Worker Configuration
MAX_RETRIES=3
PERIOD_CHECKING_SECONDS=10

# Webhook
GLIZER_WEBHOOK_URL=your_webhook_url_here
```

## 🚀 Production Deployment

For production deployment:

1. **Update environment variables** in `.env` with production values
2. **Use external Redis** for better performance and reliability
3. **Configure reverse proxy** (nginx) for the API
4. **Set up SSL certificates** for HTTPS
5. **Configure log aggregation** for monitoring
6. **Scale workers** based on load requirements

```bash
# Production example with external Redis
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🛠 Troubleshooting

### Docker Issues
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart api

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Common Issues

**Redis Connection Error:**
- Ensure Redis container is healthy: `docker-compose ps`
- Check Redis logs: `docker-compose logs redis`

**Transaction Processing Issues:**
- Check worker logs: `docker-compose logs worker1`
- Verify environment variables are set correctly
- Ensure Chrome/ChromeDriver is working in container

**API Not Responding:**
- Verify port 8000 is not in use
- Check API logs for startup errors
- Ensure database directory is writable

## 📋 Development

### Adding New Features
1. Update the code in `src/`
2. If using Docker: `docker-compose build` and `docker-compose up -d`
3. If manual setup: restart the affected services

### Database Migration
The SQLite database will be created automatically on first run. Database files are persisted in the `./data` directory.

### Testing
```bash
# Run tests (if available)
python -m pytest

# Test API endpoints
curl "http://localhost:8000/health"
```

---

**Response time:** 10-20 seconds  
**Default ports:** API: 8000, Webhook: 8001, RQ Dashboard: 9181
