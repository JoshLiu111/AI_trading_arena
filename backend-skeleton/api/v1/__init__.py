# backend/api/v1/__init__.py

from api.v1.account import router as account_router
from api.v1.stock import router as stock_router
from api.v1.competition import router as competition_router
from api.v1.trading import router as trading_router

__all__ = [
    "account_router",
    "stock_router",
    "competition_router",
    "trading_router"
]

