"""
Orbit SDK Client
Core client for sending events to Orbit API
"""

import asyncio
import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import httpx

from .types import OrbitConfig, OrbitEvent, OrbitResponse, WrapperOptions

logger = logging.getLogger("orbit")

T = TypeVar("T")


class OrbitClient:
    """
    Core Orbit client for tracking LLM usage.

    Usage:
        client = OrbitClient(OrbitConfig(api_key="orb_live_xxx"))
        client.track(OrbitEvent(model="gpt-4o", input_tokens=100, output_tokens=50))
    """

    def __init__(self, config: OrbitConfig):
        if not config.api_key:
            raise ValueError("Orbit API key is required")

        if not config.api_key.startswith("orb_"):
            raise ValueError('Invalid Orbit API key format. Keys should start with "orb_"')

        self._config = config
        self._event_queue: List[OrbitEvent] = []
        self._lock = threading.Lock()
        self._flush_timer: Optional[threading.Timer] = None
        self._is_flushing = False
        self._http_client = httpx.Client(timeout=30.0)

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        self._log("Orbit SDK initialized")

    def _log(self, msg: str, *args: Any) -> None:
        if self._config.debug:
            logger.debug(msg, *args)

    def _warn(self, msg: str, *args: Any) -> None:
        logger.warning(msg, *args)

    def track(
        self,
        model: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        *,
        event: Optional[OrbitEvent] = None,
        **kwargs: Any,
    ) -> Optional[OrbitResponse]:
        """
        Track a single event.

        Can be called with an OrbitEvent object or with keyword arguments:
            client.track(event=OrbitEvent(...))
            client.track(model="gpt-4o", input_tokens=100, output_tokens=50)
        """
        if event is None:
            if model is None:
                raise ValueError("model is required")
            event = OrbitEvent(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                **kwargs,
            )

        enriched_event = self._enrich_event(event)

        if self._config.batch_events:
            with self._lock:
                self._event_queue.append(enriched_event)
                queue_size = len(self._event_queue)
                self._log(f"Event queued ({queue_size}/{self._config.batch_size})")

                if queue_size >= self._config.batch_size:
                    return self.flush()

                self._schedule_batch_flush()
                return None

        return self._send_events([enriched_event])

    def track_many(self, events: List[OrbitEvent]) -> Optional[OrbitResponse]:
        """Track multiple events at once."""
        enriched_events = [self._enrich_event(e) for e in events]

        if self._config.batch_events:
            with self._lock:
                self._event_queue.extend(enriched_events)
                queue_size = len(self._event_queue)
                self._log(f"{len(events)} events queued ({queue_size} total)")

                if queue_size >= self._config.batch_size:
                    return self.flush()

                self._schedule_batch_flush()
                return None

        return self._send_events(enriched_events)

    def flush(self) -> Optional[OrbitResponse]:
        """Flush all queued events immediately."""
        with self._lock:
            if self._is_flushing or not self._event_queue:
                return None

            self._is_flushing = True
            self._cancel_batch_timer()

            events = self._event_queue.copy()
            self._event_queue.clear()

        try:
            response = self._send_events(events)
            self._is_flushing = False
            return response
        except Exception as e:
            # Put events back in queue on failure
            with self._lock:
                self._event_queue = events + self._event_queue
                self._is_flushing = False
            raise e

    def track_error(
        self,
        model: str,
        error_type: str,
        error_message: str,
        **kwargs: Any,
    ) -> Optional[OrbitResponse]:
        """Track an error event."""
        return self.track(
            model=model,
            input_tokens=kwargs.pop("input_tokens", 0),
            output_tokens=0,
            status="error",
            error_type=error_type,
            error_message=error_message,
            **kwargs,
        )

    def _enrich_event(self, event: OrbitEvent) -> OrbitEvent:
        """Add default values to event."""
        if not event.feature and self._config.default_feature:
            event.feature = self._config.default_feature
        if not event.environment:
            event.environment = self._config.default_environment
        if not event.status:
            event.status = "success"
        if not event.timestamp:
            event.timestamp = datetime.utcnow().isoformat() + "Z"
        return event

    def _schedule_batch_flush(self) -> None:
        """Schedule a flush after batch_interval seconds."""
        if self._flush_timer is not None:
            return

        def flush_callback() -> None:
            try:
                self.flush()
            except Exception as e:
                self._warn(f"Batch flush failed: {e}")

        self._flush_timer = threading.Timer(
            self._config.batch_interval,
            flush_callback,
        )
        self._flush_timer.daemon = True
        self._flush_timer.start()

    def _cancel_batch_timer(self) -> None:
        """Cancel the scheduled batch flush."""
        if self._flush_timer is not None:
            self._flush_timer.cancel()
            self._flush_timer = None

    def _send_events(self, events: List[OrbitEvent]) -> OrbitResponse:
        """Send events to the Orbit API."""
        self._log(f"Sending {len(events)} event(s)")

        last_error: Optional[Exception] = None
        max_attempts = self._config.max_retries if self._config.retry else 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._http_client.post(
                    f"{self._config.base_url}/ingest",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._config.api_key}",
                    },
                    json={"events": [e.to_dict() for e in events]},
                )

                if not response.is_success:
                    error_body = response.json() if response.content else {}
                    raise Exception(error_body.get("error", f"HTTP {response.status_code}"))

                data = response.json()
                result = OrbitResponse(
                    success=data.get("success", True),
                    received=data.get("received", len(events)),
                    total_tokens=data.get("total_tokens", 0),
                    total_cost_usd=data.get("total_cost_usd", 0.0),
                    message=data.get("message", ""),
                )

                self._log(
                    f"Successfully sent {result.received} event(s), cost: ${result.total_cost_usd:.6f}"
                )
                return result

            except Exception as e:
                last_error = e
                self._warn(f"Attempt {attempt}/{max_attempts} failed: {e}")

                if attempt < max_attempts:
                    # Exponential backoff: 0.1s, 0.2s, 0.4s, ...
                    delay = 0.1 * (2 ** (attempt - 1))
                    time.sleep(delay)

        raise last_error or Exception("Failed to send events")

    def shutdown(self) -> None:
        """Shutdown the client and flush remaining events."""
        self._log("Shutting down...")
        self._cancel_batch_timer()
        self.flush()
        self._http_client.close()
        self._log("Shutdown complete")

    def __enter__(self) -> "OrbitClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.shutdown()


class Orbit(OrbitClient):
    """
    Main Orbit class with convenience methods for wrapping LLM clients.

    Usage:
        orbit = Orbit(api_key="orb_live_xxx")

        # Manual tracking
        orbit.track(model="gpt-4o", input_tokens=100, output_tokens=50)

        # Automatic tracking with OpenAI
        from openai import OpenAI
        openai = orbit.wrap_openai(OpenAI())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        config: Optional[OrbitConfig] = None,
        **kwargs: Any,
    ):
        if config is not None:
            super().__init__(config)
        elif api_key is not None:
            super().__init__(OrbitConfig(api_key=api_key, **kwargs))
        else:
            raise ValueError("Either api_key or config must be provided")

    def wrap_openai(
        self,
        client: T,
        default_options: Optional[WrapperOptions] = None,
    ) -> T:
        """
        Wrap an OpenAI client for automatic tracking.

        Usage:
            from openai import OpenAI
            openai = orbit.wrap_openai(OpenAI(), WrapperOptions(feature="chat"))
        """
        from .wrappers.openai import wrap_openai

        return wrap_openai(client, self, default_options)

    def wrap_anthropic(
        self,
        client: T,
        default_options: Optional[WrapperOptions] = None,
    ) -> T:
        """
        Wrap an Anthropic client for automatic tracking.

        Usage:
            from anthropic import Anthropic
            anthropic = orbit.wrap_anthropic(Anthropic(), WrapperOptions(feature="chat"))
        """
        from .wrappers.anthropic import wrap_anthropic

        return wrap_anthropic(client, self, default_options)
