# 🎮 PUBG Recharge Bot API

Automated bot for PUBG Mobile recharges with simple and efficient REST API.

## 🚀 **Quick Installation**

### **1. Prerequisites**
- Python 3.8+
- Chrome/Chromium installed
- ChromeDriver in PATH

### **2. Installation**
```bash
# Clone the project
git clone <-repo>
cd glizer-project

# Install dependencies
pip install -r requirements.txt
```

### **3. Startup**
```bash
cd src
python main.py
```

API will be available at: `http://localhost:8000`

## 📡 **API Endpoints**

### **Create a Transaction**
```bash
curl -X POST "http://localhost:8000/transaction/create" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your_password",
    "player_id": "123456789",
    "redeem_codes": ["CODE1"]
  }'
```

**Response:**
```json
{
  "transaction_id": "transaction-uuid",
  "status": "pending",
  "message": "Transaction created and queued for processing"
}
```

### **Check Transaction Status**
```bash
curl "http://localhost:8000/transaction/{transaction_id}"
```

**Response:**
```json
{
  "transaction_id": "transaction-uuid",
  "status": "success",
  "created_at": "2024-01-15T10:30:00",
  "started_at": "2024-01-15T10:30:05",
  "completed_at": "2024-01-15T10:32:15",
  "retry_count": 0,
  "max_retries": 3,
  "result": {
    "CODE1": true,
    "CODE2": true,
    "CODE3": false
  },
  "error_message": null
}
```

### **List Transactions**
```bash
curl "http://localhost:8000/transactions?limit=50"
```

### **System Statistics**
```bash
curl "http://localhost:8000/stats"
```

**Response:**
```json
{
  "total_transactions": 150,
  "success_rate": 75.5,
  "status_breakdown": {
    "pending": 5,      // Pending
    "processing": 2,   // Processing
    "success": 110,    // Successful
    "failed": 33       // Failed after 3 attempts
  },
  "thread_manager": {
    "running": true,
    "active_threads": 1,
    "max_workers": 1,
    "pending_transactions": 5,
    "processing_transactions": 2
  }
}
```

### **Reset Database**
```bash
curl -X POST "http://localhost:8000/reset-database"
```

### **Check System Health**
```bash
curl "http://localhost:8000/health"
```

## 📊 **Transaction Statuses**

| Status | Description |
|--------|-------------|
| `pending` | Pending processing |
| `processing` | Currently executing |
| `success` | Successful (even partially) |
| `failed` | Failed after 3 attempts |

## 🔄 **Retry System**

- **Maximum 3 attempts** per transaction
- **Automatic retry** in case of temporary failure
- **Partial success**: If 2 out of 3 codes succeed, the transaction is marked as `success`

## 📁 **Project Structure**

```
glizer-project/
├── src/
│   ├── main.py              # Main FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # SQLite configuration
│   ├── thread_manager.py    # Thread manager
│   ├── schemas.py           # Pydantic schemas
│   ├── pubg_automation.py   # Service wrapper
│   ├── pubg/
│   │   └── service.py       # Selenium service
│   └── clean_database.py    # Cleanup script
├── data/                    # SQLite database
├── screenshots/             # Debug screenshots
├── user-data/               # Chrome user data by email
├── requirements.txt         # Python dependencies
└── README.md               # This file
```



## 🔧 **Configuration**

### **Environment Variables (optional)**
Create a `.env` file in the `src/` folder:
```env
PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/transactions.db
```

### **Database Cleanup**
```bash
cd src
python clean_database.py stats          # View statistics
python clean_database.py clean-failed   # Remove failed transactions
python clean_database.py clean-all      # Remove everything
```

## 📝 **Logs and Debug**

- **Logs**: Displayed in terminal
- **Screenshots**: Saved in `screenshots/`
- **Database**: `data/transactions.db`

## ⚡ **Performance**

- **1 worker** processes transactions in FIFO order
- **Shared user data** for the same email
- **Intelligent retry** with backoff
- **Optimized database** with SQLite


