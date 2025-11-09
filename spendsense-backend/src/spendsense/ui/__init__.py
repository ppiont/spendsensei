"""API routers for SpendSense endpoints"""

from spendsense.ui.users import router as users_router
from spendsense.ui.accounts import router as accounts_router
from spendsense.ui.transactions import router as transactions_router
from spendsense.ui.insights import router as insights_router
from spendsense.ui.feedback import router as feedback_router
from spendsense.ui.operator import router as operator_router

__all__ = ["users_router", "accounts_router", "transactions_router", "insights_router", "feedback_router", "operator_router"]
