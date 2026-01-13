"""
Zen Logs Python Client

Async Python client for Zen Logs ingestion endpoints.
"""

from .client import ZenLogsClient
from .exceptions import (
    ZenLogsConfigError,
    ZenLogsError,
    ZenLogsServiceNameRequired,
)
from .types import (
    AuditLogInput,
    AuditLogInputWithDefaults,
    AuditResult,
    BackpressureMode,
    BatchLogInput,
    BatchLogInputWithDefaults,
    EventLogInput,
    EventLogInputWithDefaults,
    LogLevel,
    Metadata,
    RetryMode,
    UsageLogInput,
    UsageLogInputWithDefaults,
    ZenLogsClientConfig,
    ZenLogsClientMetrics,
    ZenLogsLogger,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "ZenLogsClient",
    # Types
    "LogLevel",
    "AuditResult",
    "BackpressureMode",
    "RetryMode",
    "Metadata",
    "EventLogInput",
    "AuditLogInput",
    "UsageLogInput",
    "BatchLogInput",
    "EventLogInputWithDefaults",
    "AuditLogInputWithDefaults",
    "UsageLogInputWithDefaults",
    "BatchLogInputWithDefaults",
    "ZenLogsClientConfig",
    "ZenLogsClientMetrics",
    "ZenLogsLogger",
    # Exceptions
    "ZenLogsError",
    "ZenLogsConfigError",
    "ZenLogsServiceNameRequired",
    # Version
    "__version__",
]
