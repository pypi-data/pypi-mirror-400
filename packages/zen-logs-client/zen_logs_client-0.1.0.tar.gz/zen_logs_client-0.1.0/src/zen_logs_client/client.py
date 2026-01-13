"""Zen Logs async Python client."""

from __future__ import annotations

import asyncio
import random
from dataclasses import asdict
from enum import Enum
from typing import Any, Literal

import httpx

from .exceptions import ZenLogsServiceNameRequired
from .types import (
    AuditLogInput,
    AuditLogInputWithDefaults,
    BackpressureMode,
    BatchLogInputWithDefaults,
    EventLogInput,
    EventLogInputWithDefaults,
    Metadata,
    RetryMode,
    UsageLogInput,
    UsageLogInputWithDefaults,
    ZenLogsClientConfig,
    ZenLogsClientMetrics,
    ZenLogsLogger,
)


class _NoopLogger:
    """Default no-op logger."""

    def debug(self, message: str, **data: Any) -> None:
        pass

    def info(self, message: str, **data: Any) -> None:
        pass

    def warn(self, message: str, **data: Any) -> None:
        pass

    def error(self, message: str, **data: Any) -> None:
        pass


class _LogItem:
    """Internal queue item."""

    __slots__ = ("type", "payload")

    def __init__(
        self,
        type: Literal["event", "audit", "usage"],
        payload: EventLogInput | AuditLogInput | UsageLogInput,
    ) -> None:
        self.type = type
        self.payload = payload


def _clamp(n: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, n))


def _should_retry(status: int | None, modes: list[RetryMode]) -> bool:
    if status is None:
        return RetryMode.NETWORK in modes
    if status == 429:
        return RetryMode.RATE_LIMITED in modes
    if 500 <= status <= 599:
        return RetryMode.SERVER_ERROR in modes
    return False


class ZenLogsClient:
    """
    Async Python client for Zen Logs ingestion endpoints.

    Replicates the Node.js client API with Pythonic naming (snake_case).
    """

    def __init__(self, config: ZenLogsClientConfig | dict[str, Any]) -> None:
        """
        Initialize the client.

        Args:
            config: Client configuration (ZenLogsClientConfig or dict)
        """
        if isinstance(config, dict):
            # Handle snake_case from Python and camelCase from Node-style configs
            normalized = self._normalize_config(config)
            config = ZenLogsClientConfig(**normalized)

        self._config = config
        self._base_url = config.base_url.rstrip("/")
        self._token = config.token
        self._default_service_name = config.default_service_name

        # Queue and state
        self._queue: list[_LogItem] = []
        self._waiters: list[asyncio.Event] = []
        self._flushing = False
        self._closed = False
        self._flush_task: asyncio.Task[None] | None = None

        # Metrics
        self._metrics = ZenLogsClientMetrics()

        # HTTP client (lazy init)
        self._http_client: httpx.AsyncClient | None = None

        # Logger
        self._logger: ZenLogsLogger = config.logger or _NoopLogger()

        # Start flush loop
        self._start_flush_loop()

    def _normalize_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Normalize config keys to snake_case."""
        key_map = {
            "baseUrl": "base_url",
            "defaultServiceName": "default_service_name",
            "flushIntervalMs": "flush_interval_ms",
            "maxBatchSize": "max_batch_size",
            "maxQueueSize": "max_queue_size",
            "enqueueTimeoutMs": "enqueue_timeout_ms",
            "onEnqueueTimeout": "on_enqueue_timeout",
            "maxRetries": "max_retries",
            "baseBackoffMs": "base_backoff_ms",
            "maxBackoffMs": "max_backoff_ms",
            "retryOn": "retry_on",
            "enrichMetadata": "enrich_metadata",
        }
        result: dict[str, Any] = {}
        for k, v in config.items():
            new_key = key_map.get(k, k)
            result[new_key] = v
        return result

    def get_metrics(self) -> ZenLogsClientMetrics:
        """Get current client metrics."""
        return ZenLogsClientMetrics(
            enqueued=self._metrics.enqueued,
            sent=self._metrics.sent,
            dropped=self._metrics.dropped,
            blocked=self._metrics.blocked,
            retried=self._metrics.retried,
            queue_size=len(self._queue),
            last_error=self._metrics.last_error,
        )

    async def event(
        self,
        input: EventLogInputWithDefaults | dict[str, Any],
    ) -> None:
        """
        Log an event.

        Args:
            input: Event log input (EventLogInputWithDefaults or dict)
        """
        if isinstance(input, dict):
            input = EventLogInputWithDefaults(**input)

        service_name = input.service_name or self._require_default_service_name("event")
        enriched_metadata = self._apply_metadata_enrichment(input.metadata)

        payload = EventLogInput(
            service_name=service_name,
            level=input.level,
            message=input.message,
            stack_trace=input.stack_trace,
            metadata=enriched_metadata,
        )
        await self._enqueue(_LogItem(type="event", payload=payload))

    async def audit(
        self,
        input: AuditLogInputWithDefaults | dict[str, Any],
    ) -> None:
        """
        Log an audit trail entry.

        Args:
            input: Audit log input (AuditLogInputWithDefaults or dict)
        """
        if isinstance(input, dict):
            input = AuditLogInputWithDefaults(**input)

        service_name = input.service_name or self._require_default_service_name("audit")
        enriched_metadata = self._apply_metadata_enrichment(input.metadata)

        payload = AuditLogInput(
            service_name=service_name,
            action=input.action,
            user_id=input.user_id,
            resource=input.resource,
            ip_address=input.ip_address,
            user_agent=input.user_agent,
            result=input.result,
            metadata=enriched_metadata,
        )
        await self._enqueue(_LogItem(type="audit", payload=payload))

    async def usage(
        self,
        input: UsageLogInputWithDefaults | dict[str, Any],
    ) -> None:
        """
        Log a usage/performance metric.

        Args:
            input: Usage log input (UsageLogInputWithDefaults or dict)
        """
        if isinstance(input, dict):
            input = UsageLogInputWithDefaults(**input)

        service_name = input.service_name or self._require_default_service_name("usage")
        enriched_metadata = self._apply_metadata_enrichment(input.metadata)

        payload = UsageLogInput(
            service_name=service_name,
            endpoint=input.endpoint,
            method=input.method,
            duration_ms=input.duration_ms,
            status_code=input.status_code,
            user_id=input.user_id,
            metadata=enriched_metadata,
        )
        await self._enqueue(_LogItem(type="usage", payload=payload))

    async def batch(
        self,
        input: BatchLogInputWithDefaults | dict[str, Any],
    ) -> None:
        """
        Send multiple logs in batch (queued for next flush).

        Args:
            input: Batch log input with optional service_name per entry
        """
        if isinstance(input, dict):
            input = BatchLogInputWithDefaults(
                events=[
                    EventLogInputWithDefaults(**e) if isinstance(e, dict) else e
                    for e in input.get("events", [])
                ]
                if input.get("events")
                else None,
                audit=[
                    AuditLogInputWithDefaults(**a) if isinstance(a, dict) else a
                    for a in input.get("audit", [])
                ]
                if input.get("audit")
                else None,
                usage=[
                    UsageLogInputWithDefaults(**u) if isinstance(u, dict) else u
                    for u in input.get("usage", [])
                ]
                if input.get("usage")
                else None,
            )

        # Process events
        for e in input.events or []:
            svc = e.service_name or self._require_default_service_name("batch.events")
            meta = self._apply_metadata_enrichment(e.metadata)
            event_payload = EventLogInput(
                service_name=svc,
                level=e.level,
                message=e.message,
                stack_trace=e.stack_trace,
                metadata=meta,
            )
            await self._enqueue(_LogItem(type="event", payload=event_payload))

        # Process audit
        for a in input.audit or []:
            svc = a.service_name or self._require_default_service_name("batch.audit")
            meta = self._apply_metadata_enrichment(a.metadata)
            audit_payload = AuditLogInput(
                service_name=svc,
                action=a.action,
                user_id=a.user_id,
                resource=a.resource,
                ip_address=a.ip_address,
                user_agent=a.user_agent,
                result=a.result,
                metadata=meta,
            )
            await self._enqueue(_LogItem(type="audit", payload=audit_payload))

        # Process usage
        for u in input.usage or []:
            svc = u.service_name or self._require_default_service_name("batch.usage")
            meta = self._apply_metadata_enrichment(u.metadata)
            usage_payload = UsageLogInput(
                service_name=svc,
                endpoint=u.endpoint,
                method=u.method,
                duration_ms=u.duration_ms,
                status_code=u.status_code,
                user_id=u.user_id,
                metadata=meta,
            )
            await self._enqueue(_LogItem(type="usage", payload=usage_payload))

    async def flush(self) -> None:
        """Flush queued logs immediately (best-effort)."""
        await self._flush_loop_once()

    async def shutdown(self, *, timeout_ms: int = 5000) -> None:
        """
        Stop background flushing and drain the queue.

        Args:
            timeout_ms: Maximum time to wait for queue drain
        """
        self._closed = True

        # Cancel flush task
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Drain queue with timeout
        loop = asyncio.get_event_loop()
        deadline = loop.time() + (timeout_ms / 1000)

        while self._queue and loop.time() < deadline:
            await self._flush_loop_once()
            if self._queue:
                await asyncio.sleep(0.025)  # 25ms yield

        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> ZenLogsClient:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.shutdown()

    # Private methods

    def _require_default_service_name(self, context: str) -> str:
        """Get default service name or raise error."""
        if self._default_service_name:
            return self._default_service_name
        raise ZenLogsServiceNameRequired(context)

    def _apply_metadata_enrichment(self, metadata: Metadata | None) -> Metadata | None:
        """Apply metadata enrichment hook if configured."""
        if self._config.enrich_metadata:
            return self._config.enrich_metadata(metadata)
        return metadata

    def _start_flush_loop(self) -> None:
        """Start the background flush loop."""

        async def _flush_loop() -> None:
            while not self._closed:
                try:
                    await asyncio.sleep(self._config.flush_interval_ms / 1000)
                    await self._flush_loop_once()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._logger.error("flush loop error", error=str(e))

        try:
            loop = asyncio.get_running_loop()
            self._flush_task = loop.create_task(_flush_loop())
        except RuntimeError:
            # No running loop yet, will be started when first used
            pass

    def _signal_space_available(self) -> None:
        """Signal waiters that space is available."""
        if self._waiters:
            waiter = self._waiters.pop(0)
            waiter.set()

    async def _wait_for_space(self, timeout_ms: int) -> bool:
        """Wait for queue space, returns True if space became available."""
        loop = asyncio.get_event_loop()
        deadline = loop.time() + (timeout_ms / 1000)

        while len(self._queue) >= self._config.max_queue_size:
            now = loop.time()
            if now >= deadline:
                return False

            self._metrics.blocked += 1

            # Create event and wait
            waiter = asyncio.Event()
            self._waiters.append(waiter)

            remaining = deadline - now
            try:
                await asyncio.wait_for(waiter.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                pass
            finally:
                if waiter in self._waiters:
                    self._waiters.remove(waiter)

        return True

    async def _enqueue(self, item: _LogItem) -> None:
        """Add item to queue with backpressure handling."""
        if self._closed:
            self._metrics.dropped += 1
            return

        # Fast path: space available
        if len(self._queue) < self._config.max_queue_size:
            self._queue.append(item)
            self._metrics.enqueued += 1
            return

        # Backpressure handling
        match self._config.backpressure:
            case BackpressureMode.DROP_NEWEST:
                self._metrics.dropped += 1
                return

            case BackpressureMode.DROP_OLDEST:
                self._queue.pop(0)
                self._queue.append(item)
                self._metrics.enqueued += 1
                self._metrics.dropped += 1
                return

            case BackpressureMode.BLOCK:
                # Wait for space with timeout
                ok = await self._wait_for_space(self._config.enqueue_timeout_ms)
                if not ok:
                    self._metrics.dropped += 1
                    return

                self._queue.append(item)
                self._metrics.enqueued += 1

    async def _flush_loop_once(self) -> None:
        """Execute one flush cycle."""
        if self._flushing or not self._queue:
            return

        self._flushing = True
        try:
            # Drain up to max_batch_size
            batch_items = self._queue[: self._config.max_batch_size]
            del self._queue[: self._config.max_batch_size]
            self._signal_space_available()

            # Build batch payload
            batch: dict[str, list[dict[str, Any]]] = {
                "events": [],
                "audit": [],
                "usage": [],
            }

            for item in batch_items:
                payload_dict = self._payload_to_dict(item.payload)
                if item.type == "event":
                    batch["events"].append(payload_dict)
                elif item.type == "audit":
                    batch["audit"].append(payload_dict)
                elif item.type == "usage":
                    batch["usage"].append(payload_dict)

            # Remove empty arrays to reduce payload
            batch = {k: v for k, v in batch.items() if v}

            # Send with retry
            ok = await self._send_with_retry("/api/v1/batch", batch)
            if ok:
                self._metrics.sent += len(batch_items)
            else:
                self._metrics.dropped += len(batch_items)
        finally:
            self._flushing = False

    async def _send_with_retry(self, endpoint: str, payload: dict[str, Any]) -> bool:
        """Send request with exponential backoff retry."""
        attempt = 0
        last_status: int | None = None
        last_error: str | None = None

        while attempt <= self._config.max_retries:
            try:
                status = await self._post_json(endpoint, payload)
                last_status = status

                if status == 202:
                    self._metrics.last_error = None
                    return True

                if not _should_retry(status, self._config.retry_on):
                    self._metrics.last_error = f"non-retriable status {status}"
                    return False

                # Retry
                self._metrics.retried += 1
                attempt += 1
                backoff = self._compute_backoff_ms(attempt)
                self._logger.warn(
                    "zen-logs-client retrying request",
                    endpoint=endpoint,
                    status=status,
                    attempt=attempt,
                    backoff=backoff,
                )
                await asyncio.sleep(backoff / 1000)

            except Exception as e:
                last_status = None
                last_error = str(e)

                if not _should_retry(None, self._config.retry_on):
                    self._metrics.last_error = (
                        f"network error (non-retriable): {last_error}"
                    )
                    return False

                self._metrics.retried += 1
                attempt += 1
                backoff = self._compute_backoff_ms(attempt)
                self._logger.warn(
                    "zen-logs-client retrying after network error",
                    endpoint=endpoint,
                    attempt=attempt,
                    backoff=backoff,
                )
                await asyncio.sleep(backoff / 1000)

        # All retries exhausted
        if last_status is not None:
            self._metrics.last_error = f"failed after retries: status {last_status}"
        else:
            self._metrics.last_error = f"failed after retries: {last_error}"
        return False

    def _compute_backoff_ms(self, attempt: int) -> int:
        """Compute exponential backoff with jitter."""
        exp = self._config.base_backoff_ms * (2 ** (attempt - 1))
        capped = _clamp(exp, self._config.base_backoff_ms, self._config.max_backoff_ms)
        jitter = random.randint(0, min(100, capped))
        return capped + jitter

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def _post_json(self, endpoint: str, payload: dict[str, Any]) -> int:
        """POST JSON and return status code."""
        client = await self._get_http_client()

        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["X-Log-Token"] = self._token

        response = await client.post(
            f"{self._base_url}{endpoint}",
            json=payload,
            headers=headers,
        )
        return response.status_code

    def _payload_to_dict(
        self, payload: EventLogInput | AuditLogInput | UsageLogInput
    ) -> dict[str, Any]:
        """Convert dataclass payload to dict, omitting None values."""
        d = asdict(payload)
        # Convert enums to strings and remove None values
        result: dict[str, Any] = {}
        for k, v in d.items():
            if v is None:
                continue
            if isinstance(v, Enum):
                result[k] = v.value
            else:
                result[k] = v
        return result
