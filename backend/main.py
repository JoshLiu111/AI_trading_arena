# backend/main.py

"""
Stock Trading Arena - FastAPI Backend
Main entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import init_db
from api.v1.routes.account import router as account_router
from api.v1.routes.stock import router as stock_router
from api.v1.routes.competition import router as competition_router
from api.v1.routes.trading import router as trading_router
from utils.scheduler import lifespan
from config import settings

# Create FastAPI app with lifespan
app = FastAPI(
    title="Stock Trading Arena API",
    description="AI vs Human stock trading competition",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware with Vercel preview deployment support
def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed, including Vercel preview deployments"""
    if not origin:
        return False
    
    # Check explicitly configured origins
    if isinstance(settings.CORS_ORIGINS, list):
        if origin in settings.CORS_ORIGINS or "*" in settings.CORS_ORIGINS:
            return True
    elif isinstance(settings.CORS_ORIGINS, str):
        if origin == settings.CORS_ORIGINS or settings.CORS_ORIGINS == "*":
            return True
    
    # Allow all Vercel preview deployments (*.vercel.app)
    if origin.startswith("https://") and ".vercel.app" in origin:
        return True
    
    return False

# Custom CORS middleware that supports Vercel domains
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import re

class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            if origin and is_allowed_origin(origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        
        # Handle actual requests
        response = await call_next(request)
        
        if origin and is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

app.add_middleware(CustomCORSMiddleware)

# Include API routes
app.include_router(account_router)
app.include_router(stock_router)
app.include_router(competition_router)
app.include_router(trading_router)


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
