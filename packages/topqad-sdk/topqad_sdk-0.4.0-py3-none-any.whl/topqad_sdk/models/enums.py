from enum import Enum


class StatusEnum(str, Enum):
    """Status values for circuit processing."""

    WAITING = "waiting"
    DONE = "done"
    EXECUTING = "executing"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    CANCELLED = "cancelled"
    CANCEL_PENDING = "cancel_pending"


class LayoutType(str, Enum):
    """Layout type options."""

    HLA = "HLA"
    CUSTOM = "custom"


class QREMode(str, Enum):
    """Quantum Resource Estimation modes."""

    FULL = "full"
    LITE = "lite"


FINISHED_STATUSES = [
    StatusEnum.CANCEL_PENDING,
    StatusEnum.FAILED,
    StatusEnum.DONE,
    StatusEnum.CANCELLED,
]
