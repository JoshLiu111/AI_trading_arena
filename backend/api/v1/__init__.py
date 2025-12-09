# backend/api/v1/__init__.py

from api.v1.routes.account import router as account_router
from api.v1.routes.stock import router as stock_router
from api.v1.routes.competition import router as competition_router
from api.v1.routes.trading import router as trading_router

__all__ = [
    "account_router",
    "stock_router",
    "competition_router",
    "trading_router"
]


