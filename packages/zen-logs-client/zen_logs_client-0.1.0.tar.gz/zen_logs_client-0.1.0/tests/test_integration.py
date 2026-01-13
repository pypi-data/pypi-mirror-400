"""Integration tests for ZenLogsClient.

These tests require a running Zen Logs server.
Set ZEN_LOGS_URL environment variable to enable.

Example:
    ZEN_LOGS_URL=http://localhost:7777 pytest tests/test_integration.py -v
"""

import os

import pytest

from zen_logs_client import (
    AuditResult,
    LogLevel,
    ZenLogsClient,
)

ZEN_LOGS_URL = os.environ.get("ZEN_LOGS_URL")

pytestmark = pytest.mark.skipif(
    not ZEN_LOGS_URL,
    reason="ZEN_LOGS_URL not set - skipping integration tests",
)


@pytest.fixture
async def client():
    """Create a client connected to the real server."""
    client = ZenLogsClient({
        "base_url": ZEN_LOGS_URL,
        "default_service_name": "python-integration-test",
        "token": os.environ.get("LOG_AUTH_TOKEN"),
    })
    yield client
    await client.shutdown(timeout_ms=5000)


class TestIntegration:
    """Integration tests against a real Zen Logs server."""

    @pytest.mark.asyncio
    async def test_event_logging(self, client):
        """Test sending event logs to the server."""
        await client.event({
            "level": LogLevel.INFO,
            "message": "Integration test: event logging",
            "metadata": {
                "test": "test_event_logging",
                "language": "python",
            },
        })
        await client.flush()

        metrics = client.get_metrics()
        assert metrics.sent >= 1
        assert metrics.last_error is None

    @pytest.mark.asyncio
    async def test_audit_logging(self, client):
        """Test sending audit logs to the server."""
        await client.audit({
            "action": "INTEGRATION_TEST",
            "result": AuditResult.SUCCESS,
            "user_id": "test-user",
            "resource": "integration/test",
            "metadata": {
                "test": "test_audit_logging",
                "language": "python",
            },
        })
        await client.flush()

        metrics = client.get_metrics()
        assert metrics.sent >= 1
        assert metrics.last_error is None

    @pytest.mark.asyncio
    async def test_usage_logging(self, client):
        """Test sending usage logs to the server."""
        await client.usage({
            "endpoint": "/api/integration/test",
            "method": "GET",
            "duration_ms": 42,
            "status_code": 200,
            "metadata": {
                "test": "test_usage_logging",
                "language": "python",
            },
        })
        await client.flush()

        metrics = client.get_metrics()
        assert metrics.sent >= 1
        assert metrics.last_error is None

    @pytest.mark.asyncio
    async def test_batch_logging(self, client):
        """Test sending batch logs to the server."""
        await client.batch({
            "events": [
                {"level": LogLevel.DEBUG, "message": "Batch event 1"},
                {"level": LogLevel.INFO, "message": "Batch event 2"},
            ],
            "audit": [
                {"action": "BATCH_TEST", "result": AuditResult.SUCCESS},
            ],
            "usage": [
                {"endpoint": "/api/batch/test", "method": "POST", "status_code": 201},
            ],
        })
        await client.flush()

        metrics = client.get_metrics()
        assert metrics.sent >= 4
        assert metrics.last_error is None

    @pytest.mark.asyncio
    async def test_multiple_flushes(self, client):
        """Test multiple flush cycles."""
        for i in range(3):
            await client.event({
                "level": LogLevel.INFO,
                "message": f"Flush cycle {i}",
            })
            await client.flush()

        metrics = client.get_metrics()
        assert metrics.sent >= 3
        assert metrics.last_error is None

    @pytest.mark.asyncio
    async def test_error_event(self, client):
        """Test sending error events with stack traces."""
        try:
            raise ValueError("Test error for integration")
        except ValueError:
            import traceback
            await client.event({
                "level": LogLevel.ERROR,
                "message": "Test error occurred",
                "stack_trace": traceback.format_exc(),
                "metadata": {
                    "error_type": "ValueError",
                    "test": "test_error_event",
                },
            })

        await client.flush()

        metrics = client.get_metrics()
        assert metrics.sent >= 1
        assert metrics.last_error is None
