"""Custom exceptions for Zen Logs Python client."""


class ZenLogsError(Exception):
    """Base exception for Zen Logs client."""

    pass


class ZenLogsConfigError(ZenLogsError):
    """Configuration error."""

    pass


class ZenLogsServiceNameRequired(ZenLogsError):
    """service_name is required but not provided."""

    def __init__(self, context: str) -> None:
        super().__init__(
            f"service_name is required (missing default_service_name) for {context}"
        )
        self.context = context
