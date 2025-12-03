# backend/main.py

"""
Stock Trading Arena - FastAPI Backend
Main entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import init_db
from api import account_router, stock_router, competition_router, trading_router
from utils.scheduler import lifespan

# Create FastAPI app with lifespan
app = FastAPI(
    title="Stock Trading Arena API",
    description="AI vs Human stock trading competition",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(account_router)
app.include_router(stock_router)
app.include_router(competition_router)
app.include_router(trading_router)


@app.on_event("startup")
def startup():
    """Initialize database on startup"""
    init_db()
    print("🚀 Stock Trading Arena API started")


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "Stock Trading Arena",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health_check():
    """API health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
