from enum import Enum


class NotificationLevel(str, Enum):
    """Urgency/importance levels for notifications"""
    CRITICAL = "critical"
    NON_CRITICAL = "non_critical"

class NotificationCategory(str, Enum):
    """Types of notifications with metadata"""

    # Payment Notifications
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    INVOICE_READY = "invoice_ready"

    # Service Notifications
    REPAIR_REQUEST = "repair_request"
    REPAIR_UPDATE = "repair_update"
    MAINTENANCE_ALERT = "maintenance_alert"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"