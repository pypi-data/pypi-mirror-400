"""Tests for ZenLogsClient."""

import asyncio

import pytest
import respx
from httpx import Response

from zen_logs_client import (
    AuditResult,
    BackpressureMode,
    LogLevel,
    ZenLogsClient,
    ZenLogsClientConfig,
    ZenLogsServiceNameRequired,
)


class TestClientInitialization:
    """Test client initialization."""

    @pytest.mark.asyncio
    async def test_init_with_config_object(self):
        config = ZenLogsClientConfig(
            base_url="http://localhost:7777",
            default_service_name="test-service",
        )
        client = ZenLogsClient(config)
        try:
            assert client._base_url == "http://localhost:7777"
            assert client._default_service_name == "test-service"
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_init_with_dict(self):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
            "token": "secret",
        })
        try:
            assert client._base_url == "http://localhost:7777"
            assert client._default_service_name == "test-service"
            assert client._token == "secret"
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_init_with_camel_case_dict(self):
        client = ZenLogsClient({
            "baseUrl": "http://localhost:7777",
            "defaultServiceName": "test-service",
            "flushIntervalMs": 500,
        })
        try:
            assert client._base_url == "http://localhost:7777"
            assert client._default_service_name == "test-service"
            assert client._config.flush_interval_ms == 500
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_url_trailing_slash_stripped(self):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777/",
            "default_service_name": "test-service",
        })
        try:
            assert client._base_url == "http://localhost:7777"
        finally:
            await client.shutdown(timeout_ms=100)


class TestServiceNameRequired:
    """Test service name requirement."""

    @pytest.mark.asyncio
    async def test_event_requires_service_name(self):
        client = ZenLogsClient({"base_url": "http://localhost:7777"})
        try:
            with pytest.raises(ZenLogsServiceNameRequired) as exc_info:
                await client.event({
                    "level": LogLevel.ERROR,
                    "message": "Test error",
                })
            assert "event" in str(exc_info.value)
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_audit_requires_service_name(self):
        client = ZenLogsClient({"base_url": "http://localhost:7777"})
        try:
            with pytest.raises(ZenLogsServiceNameRequired) as exc_info:
                await client.audit({"action": "CREATE"})
            assert "audit" in str(exc_info.value)
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_usage_requires_service_name(self):
        client = ZenLogsClient({"base_url": "http://localhost:7777"})
        try:
            with pytest.raises(ZenLogsServiceNameRequired) as exc_info:
                await client.usage({"endpoint": "/api/test"})
            assert "usage" in str(exc_info.value)
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_default_service_name_used(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "my-service",
        })
        try:
            await client.event({
                "level": LogLevel.INFO,
                "message": "Test",
            })
            await client.flush()
        finally:
            await client.shutdown(timeout_ms=100)


class TestLogging:
    """Test logging methods."""

    @pytest.mark.asyncio
    async def test_event_logging(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
        })
        try:
            await client.event({
                "level": LogLevel.ERROR,
                "message": "Database error",
                "stack_trace": "Traceback...",
                "metadata": {"db": "postgres"},
            })
            await client.flush()

            metrics = client.get_metrics()
            assert metrics.enqueued == 1
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_audit_logging(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
        })
        try:
            await client.audit({
                "action": "UPDATE_PROFILE",
                "user_id": "user-123",
                "resource": "users/123",
                "result": AuditResult.SUCCESS,
            })
            await client.flush()

            metrics = client.get_metrics()
            assert metrics.enqueued == 1
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_usage_logging(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
        })
        try:
            await client.usage({
                "endpoint": "/api/users/{id}",
                "method": "GET",
                "duration_ms": 45,
                "status_code": 200,
            })
            await client.flush()

            metrics = client.get_metrics()
            assert metrics.enqueued == 1
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_batch_logging(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
        })
        try:
            await client.batch({
                "events": [
                    {"level": LogLevel.INFO, "message": "Event 1"},
                    {"level": LogLevel.WARN, "message": "Event 2"},
                ],
                "audit": [
                    {"action": "LOGIN", "result": AuditResult.SUCCESS},
                ],
                "usage": [
                    {"endpoint": "/api/health", "method": "GET", "status_code": 200},
                ],
            })
            await client.flush()

            metrics = client.get_metrics()
            assert metrics.enqueued == 4
        finally:
            await client.shutdown(timeout_ms=100)


class TestMetrics:
    """Test metrics tracking."""

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
        })
        try:
            for i in range(5):
                await client.event({
                    "level": LogLevel.INFO,
                    "message": f"Event {i}",
                })

            await client.flush()
            metrics = client.get_metrics()

            assert metrics.enqueued == 5
            assert metrics.sent == 5
            assert metrics.dropped == 0
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_queue_size_tracking(self, mock_server):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
            "flush_interval_ms": 10000,  # Long interval to prevent auto-flush
        })
        try:
            for i in range(3):
                await client.event({
                    "level": LogLevel.INFO,
                    "message": f"Event {i}",
                })

            metrics = client.get_metrics()
            assert metrics.queue_size == 3

            await client.flush()
            metrics = client.get_metrics()
            assert metrics.queue_size == 0
        finally:
            await client.shutdown(timeout_ms=100)


class TestBackpressure:
    """Test backpressure handling."""

    @pytest.mark.asyncio
    async def test_drop_newest_backpressure(self):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
            "max_queue_size": 3,
            "backpressure": BackpressureMode.DROP_NEWEST,
            "flush_interval_ms": 10000,
        })
        try:
            for i in range(5):
                await client.event({
                    "level": LogLevel.INFO,
                    "message": f"Event {i}",
                })

            metrics = client.get_metrics()
            assert metrics.enqueued == 3
            assert metrics.dropped == 2
            assert metrics.queue_size == 3
        finally:
            await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_drop_oldest_backpressure(self):
        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
            "max_queue_size": 3,
            "backpressure": BackpressureMode.DROP_OLDEST,
            "flush_interval_ms": 10000,
        })
        try:
            for i in range(5):
                await client.event({
                    "level": LogLevel.INFO,
                    "message": f"Event {i}",
                })

            metrics = client.get_metrics()
            assert metrics.enqueued == 5
            assert metrics.dropped == 2
            assert metrics.queue_size == 3
        finally:
            await client.shutdown(timeout_ms=100)


class TestMetadataEnrichment:
    """Test metadata enrichment hook."""

    @pytest.mark.asyncio
    async def test_enrich_metadata(self, mock_server):
        def enrich(metadata):
            base = {"env": "test", "version": "1.0.0"}
            if metadata:
                base.update(metadata)
            return base

        client = ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
            "enrich_metadata": enrich,
        })
        try:
            await client.event({
                "level": LogLevel.INFO,
                "message": "Test",
                "metadata": {"custom": "value"},
            })
            await client.flush()

            # Verify the request was made (we can't easily inspect the payload
            # without more complex mocking, but at least we verify it succeeds)
            metrics = client.get_metrics()
            assert metrics.sent == 1
        finally:
            await client.shutdown(timeout_ms=100)


class TestContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_server):
        async with ZenLogsClient({
            "base_url": "http://localhost:7777",
            "default_service_name": "test-service",
        }) as client:
            await client.event({
                "level": LogLevel.INFO,
                "message": "Test",
            })
            await client.flush()

            metrics = client.get_metrics()
            assert metrics.enqueued == 1


class TestRetry:
    """Test retry logic."""

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        call_count = 0

        def handle_request(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return Response(500)
            return Response(202)

        with respx.mock(assert_all_called=False) as mock:
            mock.post("http://localhost:7777/api/v1/batch").mock(
                side_effect=handle_request
            )

            client = ZenLogsClient({
                "base_url": "http://localhost:7777",
                "default_service_name": "test-service",
                "max_retries": 3,
                "base_backoff_ms": 10,  # Fast for tests
            })
            try:
                await client.event({
                    "level": LogLevel.INFO,
                    "message": "Test",
                })
                await client.flush()

                metrics = client.get_metrics()
                assert metrics.sent == 1
                assert metrics.retried == 2  # Two retries before success
            finally:
                await client.shutdown(timeout_ms=100)

    @pytest.mark.asyncio
    async def test_non_retriable_error(self):
        with respx.mock(assert_all_called=False) as mock:
            mock.post("http://localhost:7777/api/v1/batch").mock(
                return_value=Response(400)  # Bad request - not retriable
            )

            client = ZenLogsClient({
                "base_url": "http://localhost:7777",
                "default_service_name": "test-service",
            })
            try:
                await client.event({
                    "level": LogLevel.INFO,
                    "message": "Test",
                })
                await client.flush()

                metrics = client.get_metrics()
                assert metrics.dropped == 1
                assert metrics.retried == 0
            finally:
                await client.shutdown(timeout_ms=100)
