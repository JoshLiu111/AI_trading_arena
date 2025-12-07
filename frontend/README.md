# Frontend Flow Documentation

This document describes the key data flows and API structures for the frontend application.

---

## 1. Dashboard Page - Page rendering Flow

### Data Flow
```
Dashboard Component Mount
    ↓
Parallel API Calls
    ├─→ GET /api/v1/stocks/prices
    │   └─→ Returns: { stocks: [{ ticker, price, open, high, low, volume, updated_at }] }
    ├─→ GET /api/v1/accounts
    │   └─→ Returns: [{ id, account_name, display_name, account_type, balance, total_value }]
    └─→ GET /api/v1/competition/status
        └─→ Returns: { is_running, is_paused, started_at, last_trade_at }
    ↓
Price Fallback Logic (if price is null)
    └─→ GET /api/v1/stocks/{ticker}/history?days=1
        └─→ Use latest close price as current_price
    ↓
Filter & Sort Stocks
    ↓
Render StockCard Components
```

### API Data Structures examples

**GET /api/v1/stocks/prices**
```json
{
  "stocks": [
    {
      "ticker": "AAPL",
      "price": 150.25,
      "open": 149.50,
      "high": 151.00,
      "low": 149.00,
      "volume": 1000000,
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "updated_at": "2025-01-15T10:30:00Z",
  "stock_pool": ["AAPL", "MSFT", "GOOGL", ...]
}
```

**GET /api/v1/stocks/{ticker}/history?days=7**
```json
{
  "ticker": "AAPL",
  "data": [
    {
      "date": "2025-01-15",
      "open": 149.50,
      "high": 151.00,
      "low": 149.00,
      "close": 150.25,
      "volume": 1000000,
      "adj_close": 150.25
    }
  ]
}
```

---

## 2. Dashboard - Competition Start Flow

### Data Flow
```
User clicks "Start Competition"
    ↓
Navigate to Step 2 (Generate Strategy Report)
    ↓
User clicks "Generate Strategy Report"
    ↓
POST /api/v1/competition/generate-strategy?account_id={id}
    ├─→ Calculate metrics from existing stock data
    ├─→ Generate AI strategy (OpenAI API)
    └─→ Save strategy to database
    └─→ Returns: { success: true, message: "Strategy generated", strategies_created: 1 }
    ↓
GET /api/v1/trading/strategy/{account_id}
    └─→ Returns: { account_id, content: {...}, strategy_content: "...", selected_stocks: "..." }
    ↓
Display strategy content
    ↓
User clicks "Regenerate Strategy Report" (optional)
    ↓
POST /api/v1/competition/regenerate-strategy?account_id={id}
    ├─→ Delete all existing strategies for account
    ├─→ Calculate metrics from existing stock data
    ├─→ Generate new AI strategy
    └─→ Returns: { success: true, strategies_deleted: 1, strategies_created: 1 }
    ↓
GET /api/v1/trading/strategy/{account_id}
    └─→ Display new strategy
    ↓
User clicks "Start Trading"
    ↓
POST /api/v1/competition/start
    ├─→ Reset all accounts (balance = $1,000,000)
    ├─→ Clear all transactions
    ├─→ Refresh 7-day stock data from yfinance
    ├─→ Calculate metrics
    ├─→ Generate AI strategies
    └─→ Set is_running = true
    └─→ Returns: { success: true, message: "Competition started", accounts: [...] }
    ↓
GET /api/v1/competition/status
    └─→ Returns: { is_running: true, is_paused: false, started_at: "...", last_trade_at: null }
    ↓
Update Dashboard state
    ↓
Auto-navigate to Step 3 (Trading Control)
```

### API Data Structures

**POST /api/v1/competition/generate-strategy**
```json
Request: (query param) ?account_id=2
Response: {
  "success": true,
  "message": "Strategy generated",
  "strategies_created": 1
}
```

**POST /api/v1/competition/regenerate-strategy**
```json
Request: (query param) ?account_id=2
Response: {
  "success": true,
  "message": "Strategy regenerated",
  "strategies_deleted": 1,
  "strategies_created": 1
}
```

**POST /api/v1/competition/start**
```json
Response: {
  "success": true,
  "message": "Competition started",
  "accounts": [
    {
      "id": 1,
      "account_name": "human_player",
      "display_name": "Human Player",
      "account_type": "human",
      "balance": 1000000.00,
      "total_value": 1000000.00
    }
  ]
}
```

**GET /api/v1/competition/status**
```json
{
  "is_running": true,
  "is_paused": false,
  "started_at": "2025-01-15T10:30:00Z",
  "last_trade_at": "2025-01-15T10:40:00Z"
}
```

**GET /api/v1/trading/strategy/{account_id}**
```json
{
  "account_id": 2,
  "content": {
    "strategy": "Trading strategy summary",
    "selected_stocks": ["AAPL", "MSFT", "GOOGL"],
    "actions": [
      {
        "ticker": "AAPL",
        "action": "BUY",
        "quantity": 10,
        "rationale": "Strong fundamentals"
      }
    ]
  },
  "strategy_content": "{...}",
  "selected_stocks": "AAPL,MSFT,GOOGL"
}
```

---

## 3. Dashboard - Account Flow

### Data Flow
```
Dashboard Load
    ↓
GET /api/v1/accounts
    └─→ Returns: [{ id, account_name, display_name, account_type, balance, total_value, created_at }]
    ↓
Render AccountCard Components
    ↓
User clicks AccountCard
    ↓
Navigate to /account/{accountId}
```

### API Data Structures

**GET /api/v1/accounts**
```json
[
  {
    "id": 1,
    "account_name": "human_player",
    "display_name": "Human Player",
    "account_type": "human",
    "balance": 1000000.00,
    "initial_balance": 1000000.00,
    "total_value": 1050000.00,
    "created_at": "2025-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "account_name": "openai_player",
    "display_name": "OpenAI Player",
    "account_type": "ai",
    "balance": 1000000.00,
    "initial_balance": 1000000.00,
    "total_value": 1020000.00,
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

---

## 4. Account - AccountDetail Page Flow

### Data Flow
```
User clicks AccountCard
    ↓
Navigate to /account/{accountId}
    ↓
AccountDetail Component Mount
    ↓
Parallel API Calls
    ├─→ GET /api/v1/accounts/{id}
    │   └─→ Returns: { id, account_name, display_name, account_type, balance, total_value, ... }
    ├─→ GET /api/v1/accounts/{id}/positions
    │   └─→ Returns: { account_id, balance, positions: { "AAPL": {...}, "MSFT": {...} }, total_value }
    └─→ GET /api/v1/accounts/{id}/transactions
        └─→ Returns: [{ id, ticker, action, quantity, price, total_amount, executed_at, ... }]
    ↓
Transform positions object to array
    ↓
Render Account Overview, Positions Table, Transactions Table
```

### API Data Structures

**GET /api/v1/accounts/{id}**
```json
{
  "id": 1,
  "account_name": "human_player",
  "display_name": "Human Player",
  "account_type": "human",
  "balance": 950000.00,
  "initial_balance": 1000000.00,
  "total_value": 1050000.00,
  "created_at": "2025-01-15T10:00:00Z"
}
```

**GET /api/v1/accounts/{id}/positions**
```json
{
  "account_id": 1,
  "balance": 950000.00,  // Updated account balance (used to refresh UI)
  "positions": {
    "AAPL": {
      "quantity": 10,
      "avg_price": 150.00,
      "total_cost": 1500.00
    },
    "MSFT": {
      "quantity": 5,
      "avg_price": 300.00,
      "total_cost": 1500.00
    }
  },
  "total_value": 1050000.00
}
```

**Note**: The `balance` field in the positions response is used to update the account balance in the UI after trades.

**GET /api/v1/accounts/{id}/transactions**
```json
[
  {
    "id": 1,
    "account_id": 1,
    "ticker": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "price": 150.00,
    "total_amount": 1500.00,
    "rationale": "Strong fundamentals",
    "strategy_id": null,
    "executed_at": "2025-01-15T10:30:00Z"
  }
]
```

---

## 5. StockCard Flow

### Data Flow
```
Dashboard renders StockCard
    ↓
Receive stock object
    ├─→ ticker: "AAPL"
    ├─→ name: "Apple Inc."
    ├─→ current_price: 150.25
    └─→ previous_close: 149.50 (may be null)
    ↓
Calculate price change
    └─→ percent = ((current_price - previous_close) / previous_close) * 100
    ↓
Format and display
    ├─→ Stock ticker (uppercase)
    ├─→ Stock name
    ├─→ Current price (or "N/A")
    └─→ Price change percentage (with color)
    ↓
User clicks StockCard
    ↓
Navigate to /stock/{ticker}
```

### Data Structure
```javascript
stock: {
  ticker: "AAPL",
  name: "Apple Inc.",
  current_price: 150.25,
  previous_close: 149.50,  // May be null
  open: 149.50,
  high: 151.00,
  low: 149.00,
  volume: 1000000,
  updated_at: "2025-01-15T10:30:00Z"
}
```

---

## 6. StockDetail Page Flow

### Data Flow
```
User clicks StockCard
    ↓
Navigate to /stock/{ticker}
    ↓
StockDetail Component Mount
    ↓
Parallel API Calls
    ├─→ GET /api/v1/stocks/prices
    ├─→ GET /api/v1/stocks/{ticker}/history?days=7
    └─→ GET /api/v1/accounts
    ↓
Enhance stock data with history
    ├─→ Set current_price (from real-time or latest history close)
    └─→ Set previous_close (from history data)
    ↓
GET /api/v1/accounts/{humanAccountId}/positions
    └─→ Returns: { account_id, balance, positions: { "AAPL": {...}, ... }, total_value }
    ↓
Extract account balance from positions response
    └─→ setAccountBalance(positionsData.balance)
    ↓
Normalize positions object to map format
    ↓
Render Stock Info, Chart, Trade Form
    ↓
User submits trade
    ↓
POST /api/v1/trading/execute
    ├─→ Request: { account_id, ticker, action, quantity, rationale }
    └─→ Response: { id, account_id, ticker, action, quantity, price, total_amount, executed_at, ... }
    ↓
Refresh data (refreshData callback)
    ├─→ GET /api/v1/stocks/prices
    ├─→ GET /api/v1/accounts
    └─→ GET /api/v1/accounts/{id}/positions
        └─→ Extract balance: setAccountBalance(positionsData.balance)
    ↓
Update UI (balance, positions, stock price)
```

### API Data Structures

**POST /api/v1/trading/execute**
```json
Request: {
  "account_id": 1,
  "ticker": "AAPL",
  "action": "BUY",
  "quantity": 10,
  "rationale": "Strong fundamentals"
}

Response: {
  "id": 1,
  "account_id": 1,
  "ticker": "AAPL",
  "action": "BUY",
  "quantity": 10,
  "price": 150.00,
  "total_amount": 1500.00,
  "rationale": "Strong fundamentals",
  "strategy_id": null,
  "executed_at": "2025-01-15T10:30:00Z"
}
```

---

## Summary

### Key Data Transformations

1. **Positions Format**: Backend returns object `{ "AAPL": {...} }`, frontend converts to array `[{ ticker: "AAPL", ... }]` for table display

2. **Price Fallback**: If real-time price is unavailable, use latest historical `close` price

3. **Previous Close**: Calculated from history data (second-to-last day's close)

4. **Strategy Content**: Backend returns `content` (object) or `strategy_content` (JSON string), frontend parses and displays

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/stocks/prices` | GET | Get real-time prices for all stocks |
| `/stocks/{ticker}/history` | GET | Get historical price data |
| `/accounts` | GET | Get all accounts |
| `/accounts/{id}` | GET | Get account details |
| `/accounts/{id}/positions` | GET | Get account positions |
| `/accounts/{id}/transactions` | GET | Get transaction history |
| `/competition/start` | POST | Full reset + start competition |
| `/competition/generate-strategy` | POST | Generate strategy only |
| `/competition/regenerate-strategy` | POST | Delete and regenerate strategy |
| `/competition/status` | GET | Get competition status |
| `/trading/execute` | POST | Execute a trade |
| `/trading/strategy/{id}` | GET | Get latest strategy for account |