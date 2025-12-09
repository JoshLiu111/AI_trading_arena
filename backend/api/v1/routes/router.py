# backend/api/v1/router.py

"""
API v1 Router Aggregation
Combines all v1 route modules
"""

from fastapi import APIRouter
from api.v1.routes import account, competition, stock, trading

# Create main v1 router
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include all route modules
v1_router.include_router(account.router)
v1_router.include_router(competition.router)
v1_router.include_router(stock.router)
v1_router.include_router(trading.router)

__all__ = ["v1_router"]
