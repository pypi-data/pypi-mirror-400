"""Tests for type definitions."""

import pytest
from zen_logs_client import (
    AuditLogInput,
    AuditResult,
    BackpressureMode,
    EventLogInput,
    LogLevel,
    RetryMode,
    UsageLogInput,
    ZenLogsClientConfig,
    ZenLogsClientMetrics,
)


class TestEnums:
    """Test enum definitions."""

    def test_log_level_values(self):
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.WARN.value == "WARN"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.DEBUG.value == "DEBUG"

    def test_audit_result_values(self):
        assert AuditResult.SUCCESS.value == "SUCCESS"
        assert AuditResult.FAILURE.value == "FAILURE"
        assert AuditResult.PARTIAL.value == "PARTIAL"

    def test_backpressure_mode_values(self):
        assert BackpressureMode.BLOCK.value == "block"
        assert BackpressureMode.DROP_NEWEST.value == "drop_newest"
        assert BackpressureMode.DROP_OLDEST.value == "drop_oldest"

    def test_retry_mode_values(self):
        assert RetryMode.NETWORK.value == "network"
        assert RetryMode.SERVER_ERROR.value == "5xx"
        assert RetryMode.RATE_LIMITED.value == "429"


class TestDataclasses:
    """Test dataclass definitions."""

    def test_event_log_input(self):
        event = EventLogInput(
            service_name="test-service",
            level=LogLevel.ERROR,
            message="Test error",
            stack_trace="Traceback...",
            metadata={"key": "value"},
        )
        assert event.service_name == "test-service"
        assert event.level == LogLevel.ERROR
        assert event.message == "Test error"
        assert event.stack_trace == "Traceback..."
        assert event.metadata == {"key": "value"}

    def test_event_log_input_optional_fields(self):
        event = EventLogInput(
            service_name="test-service",
            level=LogLevel.INFO,
            message="Test message",
        )
        assert event.stack_trace is None
        assert event.metadata is None

    def test_audit_log_input(self):
        audit = AuditLogInput(
            service_name="test-service",
            action="CREATE",
            user_id="user-123",
            resource="users/123",
            result=AuditResult.SUCCESS,
        )
        assert audit.service_name == "test-service"
        assert audit.action == "CREATE"
        assert audit.user_id == "user-123"
        assert audit.result == AuditResult.SUCCESS

    def test_usage_log_input(self):
        usage = UsageLogInput(
            service_name="test-service",
            endpoint="/api/users",
            method="GET",
            duration_ms=45,
            status_code=200,
        )
        assert usage.service_name == "test-service"
        assert usage.endpoint == "/api/users"
        assert usage.method == "GET"
        assert usage.duration_ms == 45
        assert usage.status_code == 200


class TestConfig:
    """Test configuration dataclass."""

    def test_config_defaults(self):
        config = ZenLogsClientConfig(base_url="http://localhost:7777")
        assert config.base_url == "http://localhost:7777"
        assert config.token is None
        assert config.default_service_name is None
        assert config.flush_interval_ms == 250
        assert config.max_batch_size == 50
        assert config.max_queue_size == 2000
        assert config.backpressure == BackpressureMode.BLOCK
        assert config.enqueue_timeout_ms == 5000
        assert config.max_retries == 2
        assert config.base_backoff_ms == 200
        assert config.max_backoff_ms == 2000
        assert RetryMode.NETWORK in config.retry_on
        assert RetryMode.SERVER_ERROR in config.retry_on

    def test_config_custom_values(self):
        config = ZenLogsClientConfig(
            base_url="http://logs.example.com",
            token="secret-token",
            default_service_name="my-service",
            flush_interval_ms=500,
            max_batch_size=100,
        )
        assert config.base_url == "http://logs.example.com"
        assert config.token == "secret-token"
        assert config.default_service_name == "my-service"
        assert config.flush_interval_ms == 500
        assert config.max_batch_size == 100


class TestMetrics:
    """Test metrics dataclass."""

    def test_metrics_defaults(self):
        metrics = ZenLogsClientMetrics()
        assert metrics.enqueued == 0
        assert metrics.sent == 0
        assert metrics.dropped == 0
        assert metrics.blocked == 0
        assert metrics.retried == 0
        assert metrics.queue_size == 0
        assert metrics.last_error is None

    def test_metrics_custom_values(self):
        metrics = ZenLogsClientMetrics(
            enqueued=100,
            sent=90,
            dropped=5,
            blocked=2,
            retried=3,
            queue_size=10,
            last_error="Connection refused",
        )
        assert metrics.enqueued == 100
        assert metrics.sent == 90
        assert metrics.dropped == 5
        assert metrics.last_error == "Connection refused"
