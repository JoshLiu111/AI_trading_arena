# Stock Trading Arena

A real-time AI vs Human stock trading competition platform where users can compete against AI-powered trading strategies in a simulated stock market environment.

## Features

- **Real-time Stock Data**: Live prices and historical data for 10 major stocks (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, JPM, V, WMT)
- **AI Trading Strategy**: OpenAI-powered AI generates trading strategies based on 7-day historical data analysis
- **Automated Trading**: AI executes trades automatically every 10 minutes based on its strategy
- **Human Trading**: Manual trading interface for human players
- **Competition Management**: Start, pause, resume, and monitor trading competitions
- **Performance Tracking**: Real-time portfolio values, positions, and transaction history
- **Interactive Dashboard**: Visual charts and tables for stock prices, account balances, and trading activity

## Tech Stack

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Chart.js** - Data visualization
- **CSS3** - Styling

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Database (SQLite for local development)
- **SQLAlchemy** - ORM
- **OpenAI API** - AI strategy generation
- **yfinance** - Stock market data
- **Gunicorn** - Production WSGI server

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                         │
│  React + Vite                                                │
│  - Dashboard                                                 │
│  - Stock Details                                             │
│  - Account Management                                        │
│  - Competition Control                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (Render)                        │
│  FastAPI + PostgreSQL                                        │
│  - Account Management                                        │
│  - Stock Data Service                                        │
│  - Competition Control                                       │
│  - Trading Execution                                         │
│  - AI Strategy Generation                                    │
│  - Background Scheduler (Auto-trading)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                               │
│  - OpenAI API (Strategy Generation)                          │
│  - Yahoo Finance (Stock Data)                                │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
stock-trading-arena/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── app/             # Main app components
│   │   ├── features/        # Feature modules
│   │   │   ├── account/     # Account management
│   │   │   ├── competition/ # Competition flow
│   │   │   ├── dashboard/   # Dashboard
│   │   │   └── stock/       # Stock components
│   │   ├── lib/             # Utilities and API clients
│   │   ├── pages/           # Page components
│   │   └── ui/              # UI components
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json          # Vercel deployment config
│
├── backend/                  # FastAPI backend application
│   ├── api/                  # API routes
│   │   └── v1/
│   │       └── routes/      # Route handlers
│   ├── models/              # Database models and CRUD
│   ├── services/            # Business logic
│   │   ├── competition/    # Competition services
│   │   └── datasource/     # Data source services
│   ├── schemas/            # Pydantic schemas
│   ├── utils/              # Utilities (scheduler)
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   └── render.yaml        # Render deployment config
│
└── DEPLOYMENT.md           # Deployment guide
```

## Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **PostgreSQL** (optional, SQLite used by default for local development)
- **OpenAI API Key** (for AI strategy generation)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-trading-arena
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   echo "DATABASE_URL=sqlite:///./stock_arena.db" >> .env
   
   # Run the backend
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Create .env file (optional, defaults to localhost:8000)
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   
   # Run the frontend
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Database Setup

- **SQLite** (default): Automatically creates database file, no setup required
- **PostgreSQL**: 
  ```bash
  # Update DATABASE_URL in backend/.env
  DATABASE_URL=postgresql://user:password@localhost:5432/stock_arena
  
  # Run database initialization (optional, tables auto-create)
  python backend/scripts/init_postgres_db.py
  ```

## Deployment

The application is designed to be deployed on:
- **Frontend**: Vercel
- **Backend**: Render

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Quick Deployment Overview

1. **Deploy Backend to Render**
   - Create PostgreSQL database on Render
   - Create Web Service from GitHub repository
   - Configure environment variables
   - Deploy

2. **Deploy Frontend to Vercel**
   - Import project from GitHub
   - Set root directory to `frontend`
   - Configure `VITE_API_BASE_URL` environment variable
   - Deploy

3. **Update CORS Configuration**
   - Update backend `CORS_ORIGINS` environment variable with Vercel frontend URL

## Development

### Running Tests

```bash
# Backend (if tests exist)
cd backend
pytest

# Frontend (if tests exist)
cd frontend
npm test
```

### Code Structure

- **Frontend**: Feature-based folder structure with React hooks and components
- **Backend**: Layered architecture (API → Services → CRUD → Database)
- **API**: RESTful API with versioning (`/api/v1/`)

### Key Workflows

1. **Competition Start**: Resets accounts, refreshes stock data, generates AI strategies
2. **Auto-Trading**: Background scheduler executes AI trades every 10 minutes
3. **Manual Trading**: Human players can execute trades through the UI
4. **Strategy Generation**: AI analyzes 7-day historical data and generates trading strategies

## Configuration

### Backend Environment Variables

- `DATABASE_URL` - Database connection string
- `OPENAI_API_KEY` - OpenAI API key for strategy generation
- `CORS_ORIGINS` - Allowed frontend origins (comma-separated or JSON array)
- `DEFAULT_BALANCE` - Initial account balance (default: 1000000.00)
- `TRADING_INTERVAL_MINUTES` - Auto-trading interval (default: 10)
- `HISTORY_DAYS` - Historical data days (default: 7)

### Frontend Environment Variables

- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## Documentation

- [Frontend README](./frontend/README.md) - Frontend-specific documentation and API flows
- [Backend README](./backend/README.md) - Backend API documentation and architecture
- [Deployment Guide](./DEPLOYMENT.md) - Detailed deployment instructions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the ISC License.

## Support

For issues and questions:
- Check the documentation in `frontend/README.md` and `backend/README.md`
- Review the deployment guide in `DEPLOYMENT.md`
- Open an issue on GitHub
