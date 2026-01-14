"""
Type definitions for MetricsFirst SDK
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class InteractionType(str, Enum):
    MESSAGE = "message"
    CALLBACK_QUERY = "callback_query"
    INLINE_QUERY = "inline_query"
    COMMAND = "command"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    STICKER = "sticker"
    OTHER = "other"


class ErrorSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PurchaseStatus(str, Enum):
    INITIATED = "initiated"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class CommandEventData:
    """Data for tracking bot commands"""
    user_id: int
    command: str
    command_args: Optional[str] = None
    response_time_ms: Optional[int] = None
    is_success: bool = True
    error_message: Optional[str] = None


@dataclass
class InteractionEventData:
    """Data for tracking user interactions"""
    user_id: int
    interaction_type: InteractionType = InteractionType.MESSAGE
    content_preview: Optional[str] = None
    callback_data: Optional[str] = None
    response_time_ms: Optional[int] = None


@dataclass
class ServiceEventData:
    """Data for tracking services provided"""
    user_id: int
    service_name: str
    service_type: Optional[str] = None
    is_free: bool = True
    price: float = 0.0
    currency: str = "USD"
    duration_ms: Optional[int] = None
    is_success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorEventData:
    """Data for tracking errors"""
    error_type: str
    error_message: str
    user_id: Optional[int] = None
    error_stack: Optional[str] = None
    error_code: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PurchaseEventData:
    """Data for tracking purchases"""
    user_id: int
    purchase_id: str
    price: float
    status: PurchaseStatus = PurchaseStatus.INITIATED
    tariff_id: Optional[str] = None
    tariff_name: Optional[str] = None
    currency: str = "USD"
    is_recurrent: bool = False
    recurrence_period: Optional[str] = None  # "daily", "weekly", "monthly", "yearly"
    payment_method: Optional[str] = None
    payment_provider: Optional[str] = None
    discount_percent: float = 0.0
    coupon_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecurringChargeEventData:
    """Data for tracking recurring subscription charges"""
    user_id: int
    subscription_id: str
    amount: float
    is_success: bool = True
    currency: str = "USD"
    payment_method: Optional[str] = None
    charge_attempt: int = 1
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    next_retry_at: Optional[str] = None


@dataclass
class UserIdentifyData:
    """Data for identifying users"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)

