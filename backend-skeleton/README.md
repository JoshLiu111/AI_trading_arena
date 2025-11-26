# Backend Skeleton

A minimal backend skeleton for the Stock Trading Arena project. Contains core structure and basic operations to build upon.

## Project Overview

### Core Concept
A stock trading competition platform where human traders compete against AI traders using real market data.

### Workflow

1. **Data Initialization** - Load 100 stocks from Yahoo Finance (company info, historical prices)
2. **Account Management** - Human accounts (manual trading) and AI accounts (automated trading)
3. **Trading Flow** - Execute trades, update holdings, track performance
4. **Data Updates** - Real-time prices from Alpaca, historical data from Yahoo Finance
5. **Frontend Display** - Rankings, stock lists, trading history, detailed analytics

### Key Components

- **Database**: Stores accounts, stocks, transactions, holdings, price history
- **API**: RESTful endpoints for frontend communication
- **AI Trading**: LLM-powered traders (Claude, Gemini, Groq, OpenAI)
- **Scheduler**: Automated task runner for AI trading and data updates
- **Data Sources**: Yahoo Finance (historical), Alpaca (real-time)

## Implementation Checklist

To make the skeleton fully functional, you need to implement the following:

### Core Tasks (Required for Frontend)

1. **Create `routers/trading.py`**
   - Implement `POST /api/trading/execute` endpoint
   - Handle trade validation, execution, and account/holdings updates

2. **Create `models/analytics_models.py`**
   - Add `PortfolioSnapshot` model (for account performance charts)
   - Add `AIDecisionLog` model (for AI trading decision logs)

3. **Extend `routers/accounts.py`**
   - Add `GET /api/accounts/{id}/snapshots` endpoint
   - Add `GET /api/accounts/{id}/ai-logs` endpoint

4. **Implement Data Services** (recommended)
   - Create `services/data_sources/yahoo_service.py` for Yahoo Finance integration
   - Create `services/data_sources/alpaca_service.py` for real-time prices
   - Or use `yfinance` directly in scripts (simpler, but less organized)

### Optional Tasks (Recommended)

5. **Create `routers/competition.py`**
   - Implement `POST /api/competition/reset` endpoint

6. **Create `routers/scheduler.py`**
   - Implement scheduler control endpoints (start/stop/status)

7. **Create `utils/scheduler.py`**
   - Implement `TradingScheduler` class for automated AI trading

8. **Enhance Trading Rules**
   - Add `trades_today` counter to `Account` model
   - Add competition date tracking fields
   - Implement daily trade limit validation

**Note**: The skeleton provides the foundation. Focus on core tasks first, then add optional features as needed.

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp env.example .env
# Edit .env with your database URL and API keys

# 4. Initialize database
python init_db.py

# 5. Initialize 100 stocks (optional but recommended)
python scripts/init_stocks.py

# 6. Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend-skeleton/
├── ai/                      # AI trading module
│   ├── base_trader.py       # Base trader class
│   ├── trading_engine.py   # Trading execution engine
│   ├── llm_clients/         # LLM clients (Claude, Gemini, Groq, OpenAI)
│   ├── prompts/            # Trading prompt templates
│   └── traders/             # AI trader implementations
├── config/
│   ├── settings.py          # Configuration settings
│   └── stock_list.py        # 100 stock tickers list
├── models/
│   ├── database.py          # Database connection
│   ├── deps.py              # FastAPI dependencies
│   ├── account_models.py    # Account, Holding, Transaction
│   └── stock_models.py       # Stock, StockDailyData
├── routers/
│   ├── accounts.py          # Account API endpoints
│   └── stocks.py            # Stock API endpoints
├── scripts/
│   └── init_stocks.py       # Initialize 100 stocks from Yahoo Finance
├── main.py                  # FastAPI app entry point
├── init_db.py              # Database initialization
├── requirements.txt         # Dependencies
└── env.example             # Environment template
```

## Setup & Configuration

### Data Sources

**Yahoo Finance** (Primary - FREE)
- No API key needed (uses `yfinance`)
- Historical prices, company info, financial metrics

**Alpaca** (Real-time Prices)
- Sign up at https://alpaca.markets/ (free tier available)
- Add to `.env`: `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`
- Required for real-time price updates

**Polygon.io** (Optional Backup)
- Can be omitted - only needed as backup data source

**Note**: Minimum setup only needs Yahoo Finance. Alpaca is recommended for real-time prices.

### Database & Models

The skeleton includes simplified database models:

- **Account**: User accounts (human or AI) with balance and total value
- **Holding**: Stock positions with quantity, avg cost, current price
- **Transaction**: Trade records with action, price, quantity, rationale
- **Stock**: Company basic information (ticker, name, sector, market cap...)
- **StockDailyData**: Historical price data (date, open, high, low, close, volume...)

See `models/` directory for model definitions.

## API & Implementation

**Important**: You can build your backend however you want - I can adjust the frontend to match your API design. Below is what my frontend currently uses as a reference.

### Core Endpoints

#### Accounts
- `GET /api/accounts/` - List all accounts
- `GET /api/accounts/{id}/holdings` - Get holdings
- `GET /api/accounts/{id}/transactions` - Get transaction history
- `GET /api/accounts/{id}/snapshots` - Portfolio snapshots (for charts)

#### Stocks
- `GET /api/stocks/` - List all stocks
- `GET /api/stocks/list` - List tickers only
- `GET /api/stocks/{ticker}` - Stock detail
- `GET /api/stocks/{ticker}/history` - Price history
- `GET /api/stocks/{ticker}/financials` - Financial metrics

#### Trading
- `POST /api/trading/execute` - Execute trade

### Optional Endpoints

- `GET /api/accounts/{id}/ai-logs` - AI decision logs
- `GET /api/scheduler/status` - Scheduler status
- `POST /api/scheduler/start` - Start scheduler
- `POST /api/scheduler/stop` - Stop scheduler
- `POST /api/competition/reset` - Reset competition

### Implementation Requirements

To support the API endpoints above, you'll need to implement:

**Core (Required):**
1. **`routers/trading.py`** - Implement `POST /api/trading/execute`
2. **`models/analytics_models.py`** - Add `PortfolioSnapshot` and `AIDecisionLog` models
3. Add snapshots and ai-logs endpoints to `routers/accounts.py`

**Optional (Recommended):**
4. **`routers/competition.py`** - Competition management
5. **`routers/scheduler.py`** - Scheduler control

**Note**: The skeleton provides basic structure. You need to implement these routers and models to support the full frontend functionality.

## Trading System

### Human Trading

Users can manually execute trades through the frontend:
1. Select stock and action (Buy/Sell)
2. Enter quantity and rationale
3. Trade is validated and executed
4. Account balance and holdings are updated

### AI Trading

AI traders use LLM models to analyze market conditions and make trading decisions.

#### Available LLM Models (FREE tiers available)

1. **Claude** (Anthropic) - FREE tier
   - Sign up: https://console.anthropic.com/
   - Model: `claude-3-haiku-20240307`
   - Setup: Add `ANTHROPIC_API_KEY` to `.env`
   ```python
   from ai.traders.claude_trader import ClaudeTrader
   trader = ClaudeTrader(account_id=1)
   ```

2. **Gemini** (Google) - FREE tier
   - Sign up: https://aistudio.google.com/
   - Model: `gemini-2.0-flash-exp`
   - Setup: Add `GOOGLE_API_KEY` to `.env`

3. **Groq** - FREE tier (very fast)
   - Sign up: https://console.groq.com/
   - Model: `llama-3.3-70b-versatile`
   - Setup: Add `GROQ_API_KEY` to `.env`

4. **OpenAI** (Paid, optional)
   - Model: `gpt-4o-mini` or `gpt-4`
   - Setup: Add `OPENAI_API_KEY` to `.env`

#### Usage Example

```python
from ai.traders.claude_trader import ClaudeTrader
from ai.trading_engine import TradingEngine
from models.database import get_session

trader = ClaudeTrader(account_id=1)
engine = TradingEngine()

with get_session() as session:
    market_data = {"AAPL": 150.0, "MSFT": 350.0}
    result = engine.run_trader(session, trader, account_id=1, market_data=market_data)
    print(result)
```

#### Quick Setup

1. Choose a FREE LLM provider (Claude, Gemini, or Groq recommended)
2. Sign up and get API key
3. Add to `.env`: `ANTHROPIC_API_KEY=your_key` (or `GOOGLE_API_KEY`, `GROQ_API_KEY`)
4. Install package: `pip install anthropic` (or `google-generativeai`, `groq`)

### Scheduler (Optional)

For automated AI trading, implement a scheduler that:
1. Fetches real-time prices from Alpaca
2. Updates holdings with current market values
3. Runs AI traders to make decisions
4. Executes trades automatically
5. Records portfolio snapshots

### Trading Rules & Competition Settings

**Trading Frequency:**
- **Testing Phase**: Higher frequency acceptable (e.g., every 1-5 minutes) for rapid testing
- **Production/Competition**: Set daily trading limits (e.g., max 3-5 trades per account per day)

**Competition Duration:**
- **Short-term**: 1 week (7 days) - Good for quick competitions and testing
- **Long-term**: 1 month (30 days) - Better for evaluating long-term strategies

**Implementation Notes:**
- Add `trades_today` counter to `Account` model for daily trade limits
- Add `competition_start_date` and `competition_end_date` to track periods
- Implement validation in trading endpoints to enforce frequency limits
- Record portfolio snapshots daily at market close for fair comparison

## Development Guide

### Development Notes

- Minimal skeleton - You can add your own business logic
- Database models are simplified versions
- CRUD operations are basic examples - extend as needed
- AI module is optional - install LLM packages as needed

### What You Can Work On

- Add more API endpoints in `routers/`
- Implement data fetching services (Yahoo Finance, Alpaca, etc.)
- Create data update scripts
- Build scheduler services for automated trading
- Work on AI traders' workflow and strategies
- Implement analytics and portfolio tracking

The codebase is modular - feel free to build features as needed!
