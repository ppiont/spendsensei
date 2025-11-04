"""API routers for SpendSense endpoints"""

from spendsense.routers.users import router as users_router
from spendsense.routers.accounts import router as accounts_router
from spendsense.routers.transactions import router as transactions_router

__all__ = ["users_router", "accounts_router", "transactions_router"]
