"""
MetricsFirst SDK for Python
Track analytics for your Telegram bots
"""

from .client import MetricsFirst
from .async_client import AsyncMetricsFirst
from .types import (
    ServiceEventData,
    ErrorEventData,
    ErrorSeverity,
    PurchaseEventData,
    PurchaseStatus,
    RecurringChargeEventData,
    UserIdentifyData,
)

__version__ = "0.1.1"
__all__ = [
    "MetricsFirst",
    "AsyncMetricsFirst",
    "ServiceEventData",
    "ErrorEventData",
    "ErrorSeverity",
    "PurchaseEventData",
    "PurchaseStatus",
    "RecurringChargeEventData",
    "UserIdentifyData",
]

