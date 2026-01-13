"""Type definitions for Zen Logs Python client."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class LogLevel(str, Enum):
    """Log severity levels."""

    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"


class AuditResult(str, Enum):
    """Audit action result types."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"


class BackpressureMode(str, Enum):
    """Queue backpressure handling modes."""

    BLOCK = "block"
    DROP_NEWEST = "drop_newest"
    DROP_OLDEST = "drop_oldest"


class RetryMode(str, Enum):
    """Retry condition modes."""

    NETWORK = "network"
    SERVER_ERROR = "5xx"
    RATE_LIMITED = "429"


# JSON-compatible metadata type
Metadata = dict[str, Any]


@dataclass
class EventLogInput:
    """Event log input payload."""

    service_name: str
    level: LogLevel
    message: str
    stack_trace: str | None = None
    metadata: Metadata | None = None


@dataclass
class EventLogInputWithDefaults:
    """Event log input with optional service_name (uses default)."""

    level: LogLevel
    message: str
    service_name: str | None = None
    stack_trace: str | None = None
    metadata: Metadata | None = None


@dataclass
class AuditLogInput:
    """Audit log input payload."""

    service_name: str
    action: str
    user_id: str | None = None
    resource: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    result: AuditResult | None = None
    metadata: Metadata | None = None


@dataclass
class AuditLogInputWithDefaults:
    """Audit log input with optional service_name (uses default)."""

    action: str
    service_name: str | None = None
    user_id: str | None = None
    resource: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    result: AuditResult | None = None
    metadata: Metadata | None = None


@dataclass
class UsageLogInput:
    """Usage log input payload."""

    service_name: str
    endpoint: str
    method: str | None = None
    duration_ms: int | None = None
    status_code: int | None = None
    user_id: str | None = None
    metadata: Metadata | None = None


@dataclass
class UsageLogInputWithDefaults:
    """Usage log input with optional service_name (uses default)."""

    endpoint: str
    service_name: str | None = None
    method: str | None = None
    duration_ms: int | None = None
    status_code: int | None = None
    user_id: str | None = None
    metadata: Metadata | None = None


@dataclass
class BatchLogInput:
    """Batch log input payload."""

    events: list[EventLogInput] | None = None
    audit: list[AuditLogInput] | None = None
    usage: list[UsageLogInput] | None = None


@dataclass
class BatchLogInputWithDefaults:
    """Batch log input with optional service_name on each entry."""

    events: list[EventLogInputWithDefaults] | None = None
    audit: list[AuditLogInputWithDefaults] | None = None
    usage: list[UsageLogInputWithDefaults] | None = None


class ZenLogsLogger(Protocol):
    """Protocol for custom loggers."""

    def debug(self, message: str, **data: Any) -> None: ...
    def info(self, message: str, **data: Any) -> None: ...
    def warn(self, message: str, **data: Any) -> None: ...
    def error(self, message: str, **data: Any) -> None: ...


@dataclass
class ZenLogsClientMetrics:
    """Client metrics for observability."""

    enqueued: int = 0
    sent: int = 0
    dropped: int = 0
    blocked: int = 0
    retried: int = 0
    queue_size: int = 0
    last_error: str | None = None


@dataclass
class ZenLogsClientConfig:
    """Client configuration options."""

    # Required
    base_url: str

    # Optional authentication
    token: str | None = None

    # Service defaults
    default_service_name: str | None = None

    # Flush settings
    flush_interval_ms: int = 250
    max_batch_size: int = 50
    max_queue_size: int = 2000

    # Backpressure settings
    backpressure: BackpressureMode = BackpressureMode.BLOCK
    enqueue_timeout_ms: int = 5000
    on_enqueue_timeout: str = "drop_newest"

    # Retry settings
    max_retries: int = 2
    base_backoff_ms: int = 200
    max_backoff_ms: int = 2000
    retry_on: list[RetryMode] = field(
        default_factory=lambda: [RetryMode.NETWORK, RetryMode.SERVER_ERROR]
    )

    # Optional hooks
    logger: ZenLogsLogger | None = None
    enrich_metadata: Callable[[Metadata | None], Metadata | None] | None = None
