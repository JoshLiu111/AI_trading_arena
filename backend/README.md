# Stock Trading Arena - FastAPI Backend

AI vs Human Stock Trading Competition Backend API

## 📁 Project Structure

```
stock-arena-backend/
├── main.py                    # FastAPI entry point + CORS + route registration
├── config.py                  # Configuration (stock pool, trading interval, etc.)
├── models/                    # Database models and CRUD operations
│   ├── __init__.py
│   ├── database.py            # Database connection
│   ├── schema/                # SQLAlchemy models
│   └── crud/                  # CRUD operations
├── schemas/                   # Pydantic request/response models
│   └── __init__.py
├── services/                  # Business logic layer
│   ├── datasource/            # Data source services
│   │   ├── base_data_source.py              # Abstract data source interface
│   │   ├── data_source_factory.py          # Data source factory (Polygon.io)
│   │   ├── stock_price_service.py          # Stock price service (uses Polygon.io)
│   │   ├── polygon_service.py              # Polygon.io REST API data source
│   │   ├── polygon_websocket_service.py    # Polygon.io WebSocket for real-time data
│   │   └── refresh_historical_data_service.py  # Refresh and save historical data
│   └── competition/           # Competition-related services
│       ├── ai_strategy_report_service.py  # GPT strategy generation
│       ├── competition_manage_service.py  # Competition state management
│       ├── generate_metrics_service.py     # 7-day metrics calculation (price change, volatility, trend)
│       └── trading_service.py             # Execute trades + position calculation
├── api/                       # API routes
│   └── v1/                    # API version 1
│       ├── account.py         # Account API
│       ├── stock.py           # Stock API
│       ├── competition.py     # Competition API
│       └── trading.py         # Trading API
└── utils/
    └── scheduler.py           # Auto-trading every 10 minutes
```

## 🔌 API Endpoints Summary

### Accounts `/api/v1/accounts` -> For frontend account cards.

| Method | Endpoint | Function |
|--------|----------|----------|
| GET | `/api/v1/accounts` | All accounts (Frontend Section 1) |
| GET | `/api/v1/accounts/{id}` | Get account details |
| GET | `/api/v1/accounts/{id}/transactions` | Transaction history |
| GET | `/api/v1/accounts/{id}/positions` | Current positions |

### Stocks `/api/v1/stocks`    -> For frontend stock cards.

| Method | Endpoint | Function |
|--------|----------|----------|
| GET | `/api/v1/stocks/prices` | Real-time prices for 10 stocks (Frontend Section 2) |
| GET | `/api/v1/stocks/{ticker}/history` | Historical K-line data |

### Competition `/api/v1/competition`   -> For start/pause/resume competition (Optional)

| Method | Endpoint | Function |
|--------|----------|----------|
| POST | `/api/v1/competition/start` | 🚀 Start competition |
| POST | `/api/v1/competition/pause` | ⏸️ Pause trading |
| POST | `/api/v1/competition/resume` | ▶️ Resume trading |
| GET | `/api/v1/competition/status` | Competition status |

### Trading `/api/v1/trading`         -> For calling LLM automatically trading (optional)

| Method | Endpoint | Function |
|--------|----------|----------|
| POST | `/api/v1/trading/execute` | Human player trade execution |
| GET | `/api/v1/trading/strategy/{account_id}` | Get latest AI strategy for account |
| GET | `/api/v1/trading/strategies/{account_id}` | Get strategy history for account |

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (React)                                           │
│  ├── Account Section ────────► GET /api/v1/accounts             │
│  ├── Stock Section ──────────► GET /api/v1/stocks/prices        │
│  └── Competition Control ───► POST /api/v1/competition/*       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  API Routes (API Layer) ─ Receive requests, call Services  │
│  ├── account.py     → Account/positions/transaction queries  │
│  ├── stock.py       → Real-time prices/historical data       │
│  ├── competition.py → Competition control (start/pause/resume)│
│  └── trading.py     → Execute trades/view strategies         │
└─────────────────────────────────────────────────────────────┘
                              │                ---> Alternative business log: llm analysis all 10/5 stocks in the pool, return a text based trading 
                              │                      Strategy sent to the frontend.
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Services (Business Layer) ─ Core Logic                     │
│                                                             │
│  CompetitionManageService (Core Orchestrator)               │
│       │                                                     │
│       ├──► StockPriceService ────► Polygon.io (real-time prices)│  
│       ├──► RefreshHistoricalDataService ──► Refresh & save data│
│       ├──► GenerateMetricsService ──► Calculate 7-day metrics│
│       ├──► AIStrategyReportService ──► OpenAI (generate strategies)│
│       └──► TradingService ──► Execute trading logic         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CRUD (Data Layer) ─ Database Operations                    │
│  ├── account_crud     → accounts table                      │
│  ├── stock_crud       → stocks table                        │
│  ├── stock_price_crud → stock_price_data table              │
│  ├── strategy_crud    → trading_strategies table             │
│  └── transaction_crud → transactions table                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Core Workflows

### 1️⃣ Competition Start Workflow (`POST /api/v1/competition/start`)

```
1️⃣ Reset Accounts
   CompetitionManageService 
     → AccountCRUD.reset (balance=$1M, clear transactions)

2️⃣ Refresh Stock Prices
   RefreshHistoricalDataService 
     → DataSource.download_bulk(10 stocks, 7 days)  # Uses Polygon.io data source
     → StockPriceCRUD.create_price_data

3️⃣ Calculate Metrics
   GenerateMetricsService 
     → StockPriceCRUD.get_price_history
     → Output: price change %, volatility, trend

4️⃣ AI Generate Strategy
   AIStrategyReportService 
     → OpenAI (send metrics as prompt)
     → StrategyCRUD.create_strategy (store strategy JSON)

5️⃣ Start Timer
   Scheduler 
     → Trigger execute_ai_trades() every 10 minutes
```

### 2️⃣ Auto-Trading Workflow

```
Scheduler triggers
    │
    ▼
CompetitionManageService.execute_ai_trades()
    │
    ├── Check: is_running && !is_paused
    │
    └── FOR each AI account:
            │
            ├── StrategyCRUD.get_latest_strategy()
            │      ↓
            │   Strategy JSON: {actions: [{ticker, action, qty}]}
            │
            └── FOR each action:
                    │
                    TradingService.execute_trade()
                        │
                        ├── StockPriceService.get_current_price() → Polygon.io
                        ├── Validate balance/positions
                        ├── AccountCRUD.update_account() (update balance)
                        └── TransactionCRUD.create_transaction()
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment variables (optional)
# Create .env file and add:
#   DATABASE_URL=sqlite:///./stock_arena.db  # or PostgreSQL connection string
#   OPENAI_API_KEY=your_api_key_here

# 3. Run the service
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Database Setup:**
- **SQLite** (default): No setup needed - database file is created automatically
- **PostgreSQL**: Create database first, then update `DATABASE_URL` in `.env` or `config.py`

## 💻 Frontend Integration Examples

```javascript
// 1. Get real-time stock prices (Frontend Section 2)
fetch('/api/v1/stocks/prices')
  .then(res => res.json())
  .then(data => console.log(data.stocks));

// 2. Get account information (Frontend Section 1)
fetch('/api/v1/accounts')
  .then(res => res.json())
  .then(accounts => console.log(accounts));

// 3. Start competition
fetch('/api/v1/competition/start', { method: 'POST' })
  .then(res => res.json())
  .then(result => console.log(result));

// 4. Pause trading
fetch('/api/v1/competition/pause', { method: 'POST' });

// 5. Resume trading
fetch('/api/v1/competition/resume', { method: 'POST' });

// 6. Human player trade
fetch('/api/v1/trading/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    account_id: 1,
    ticker: 'AAPL',
    action: 'BUY',
    quantity: 10
  })
});

// 7. Alternative: Trading strategy report
fetch('/api/v1/trading/strategy/1', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. Create a `.env` file in the `backend` directory or set them in your deployment platform.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./stock_arena.db` | No |
| `OPENAI_API_KEY` | OpenAI API key for strategy generation | `""` | Yes (for AI features) |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated or JSON array) | `["*"]` | No |
| `DEFAULT_BALANCE` | Initial account balance | `1000000.00` | No |
| `TRADING_INTERVAL_MINUTES` | Auto-trading interval in minutes | `10` | No |
| `HISTORY_DAYS` | Historical data days to fetch | `7` | No |
| `USE_HISTORICAL_AS_REALTIME` | Use historical data as real-time (for testing) | `false` | No |
| `DATA_SOURCE` | Data source provider (only "polygon" supported) | `"polygon"` | No |
| `POLYGON_API_KEY` | Polygon.io API key (required) | `""` | Yes |

**Example `.env` file:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/stock_arena
OPENAI_API_KEY=sk-your-api-key-here
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
DEFAULT_BALANCE=1000000.00
TRADING_INTERVAL_MINUTES=10
HISTORY_DAYS=7
DATA_SOURCE=polygon
POLYGON_API_KEY=your-polygon-api-key-here
```

**CORS_ORIGINS Format:**
- Comma-separated: `https://app1.com,https://app2.com`
- JSON array: `["https://app1.com","https://app2.com"]`
- Single string: `https://app1.com`

### Application Settings

In `config.py` you can also configure:

- `DEFAULT_BALANCE`: Initial balance (default $1,000,000)
- `TRADING_INTERVAL_MINUTES`: Auto-trading interval (default 10 minutes)
- `HISTORY_DAYS`: Historical data days (default 7 days)
- `STOCK_POOL`: Stock pool (default 10 stocks: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, JPM, V, WMT)

## 🚀 Deployment

### Production Deployment on Render

The backend is configured for deployment on Render. See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed instructions.

**Quick Steps:**
1. Push code to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service from GitHub repository
4. Configure environment variables in Render Dashboard
5. Deploy

**Production Start Command:**
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Important Notes for Production:**
- Use PostgreSQL (SQLite is not suitable for production)
- Set `CORS_ORIGINS` to your actual frontend domain(s)
- Ensure `OPENAI_API_KEY` is configured
- Background scheduler runs automatically via `lifespan` (Render supports long-running services)
- Render free tier may have cold start delays (15 minutes of inactivity)

### Local Development

For local development, you can use SQLite:

```bash
# Default SQLite (no setup needed)
python main.py
```

Or use PostgreSQL:

```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/stock_arena

# Optional: Initialize database
python scripts/init_postgres_db.py

# Run the service
python main.py
```

## 📝 Notes

1. **Schema/CRUD Files**: All model files are already in `models/schema/` and CRUD operations in `models/crud/`
2. **AI API**: OpenAI API Key must be configured via `OPENAI_API_KEY` environment variable to generate strategies
3. **Scheduled Tasks**: Auto-trading runs every 10 minutes by default via `scheduler.py`, can be adjusted via `TRADING_INTERVAL_MINUTES` environment variable
4. **Database**: 
   - **SQLite** (default for local dev): Automatically creates database file, no setup required
   - **PostgreSQL** (recommended for production): Requires database creation, but tables are created automatically via `init_db()`
   - **No code changes needed** to switch between databases - just update `DATABASE_URL` environment variable
5. **Background Tasks**: The `lifespan` context manager starts the trading scheduler on application startup. This works on Render but not on serverless platforms like Vercel.
6. **Data Sources**: 
   - **Polygon.io**: Stocks Starter Plan provides unlimited API calls, 5 years historical data, and WebSocket support. Get API key at https://polygon.io/

## 🔧 Development Guide

### Module Responsibilities

- **API Routes**: Handle HTTP requests, parameter validation, call Services
- **Services**: Core business logic, coordinate multiple CRUD operations
- **CRUD**: Database operation encapsulation, return ORM objects
- **Schemas**: Pydantic models for API request/response validation

### Data Flow

1. **Frontend Request** → Router receives
2. **Router** → Calls Service method
3. **Service** → Calls multiple CRUD operations
4. **CRUD** → Operates on database
5. **Return Result** → Service → Router → Frontend
