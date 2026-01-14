"""
API Routes (FastAPI routers).
"""
from .auth_controller import router as auth_router
from .category_controller import router as category_router
from .chat_controller import router as chat_router
from .report_controller import router as report_router
from .optimization_controller import router as optimization_router
from .transaction_controller import router as transaction_router
from .user_controller import router as user_router
from .bill_controller import router as bill_router
from .deep_dive_controller import router as deep_dive_router
from .bank import router as bank_router

__all__ = [
    "auth_router",
    "category_router",
    "chat_router",
    "report_router",
    "optimization_router",
    "transaction_router",
    "user_router",
    "bill_router",
    "deep_dive_router",
    "bank_router"
]

