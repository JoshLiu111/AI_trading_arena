"""
FastAPI application entry point.
Main application file that sets up the API server, routes, and middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import accounts, stocks
from config.settings import settings

# Create FastAPI application
app = FastAPI(
    title="Stock Trading Arena API - Skeleton",
    version="1.0.0",
    description="A minimal backend skeleton for the Stock Trading Arena project",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(accounts.router)
app.include_router(stocks.router)


# Health check endpoint
@app.get("/")
def read_root():
    """
    API root endpoint.
    Returns basic API information.
    """
    return {
        "message": "Stock Trading Arena API - Skeleton is running!",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns API health status.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }

