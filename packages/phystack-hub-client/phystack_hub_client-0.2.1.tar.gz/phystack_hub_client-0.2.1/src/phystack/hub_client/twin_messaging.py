"""
Twin Messaging Factory

Creates emit/on/to methods for any twin type.
Provides a consistent messaging API across all instance types.

API Design:
- emit(type, payload): Fire-and-forget broadcast to subscribers
- to(target_id).emit(type, payload): Fire-and-forget to specific twin
- to(target_id).emit(type, payload, callback): Request-response to specific twin
- on(type, callback): Listen for messages, with optional respond callback
"""

import asyncio
import time
import random
import string
from dataclasses import dataclass
from typing import Any, Callable, Optional

from phystack.hub_client.types.twin_types import TwinMessageResult, TwinMessageResultStatus


REQUEST_TIMEOUT = 10.0  # seconds


@dataclass
class PendingRequest:
    """Pending request awaiting response."""

    future: asyncio.Future[TwinMessageResult]
    timeout_handle: Optional[asyncio.TimerHandle]


class TwinMessagingContext:
    """Context for twin messaging operations."""

    def __init__(
        self,
        send_event: Callable[[str, dict[str, Any]], None],
        on_twin_message: Callable[[str, Callable[[dict[str, Any]], None]], None],
        twin_id: str,
        device_id: str,
        type_prefix: str,
    ) -> None:
        self.send_event = send_event
        self.on_twin_message = on_twin_message
        self.twin_id = twin_id
        self.device_id = device_id
        self.type_prefix = type_prefix


class TargetedEmitter:
    """Emitter targeted at a specific twin."""

    def __init__(
        self,
        target_twin_id: str,
        send_message: Callable[[str, str, Any], None],
        send_request: Callable[[str, str, Any], "asyncio.Future[TwinMessageResult]"],
    ) -> None:
        self._target_twin_id = target_twin_id
        self._send_message = send_message
        self._send_request = send_request

    def emit(
        self,
        event_type: str,
        payload: Any = None,
        callback: Optional[Callable[[TwinMessageResult], None]] = None,
    ) -> Optional["asyncio.Future[TwinMessageResult]"]:
        """Emit an event to the targeted twin.

        Args:
            event_type: Type of event to emit.
            payload: Data to send.
            callback: Optional callback for request-response pattern.

        Returns:
            Future if callback provided, None otherwise.
        """
        if callback:
            future = self._send_request(self._target_twin_id, event_type, payload)

            # Add callback to be called when future completes
            def on_complete(f: asyncio.Future[TwinMessageResult]) -> None:
                try:
                    result = f.result()
                    callback(result)
                except Exception as e:
                    callback(TwinMessageResult(
                        status=TwinMessageResultStatus.ERROR,
                        message=str(e),
                    ))

            future.add_done_callback(on_complete)
            return future
        else:
            self._send_message(self._target_twin_id, event_type, payload)
            return None


class TwinMessaging:
    """Twin messaging methods (emit, on, to)."""

    def __init__(self, context: TwinMessagingContext) -> None:
        self._context = context
        self._pending_requests: dict[str, PendingRequest] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Set up response listener
        self._setup_response_listener()

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get the event loop, creating if necessary."""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"{int(time.time() * 1000)}-{random_part}"

    def _build_message(self, msg_type: str, data: Any) -> dict[str, Any]:
        """Build message payload with metadata."""
        return {
            "type": f"{self._context.type_prefix}:{msg_type}",
            "sourceTwinId": self._context.twin_id,
            "sourceDeviceId": self._context.device_id,
            "data": data,
        }

    def _send_message(self, target_twin_id: str, msg_type: str, payload: Any) -> None:
        """Send fire-and-forget event."""
        self._context.send_event(target_twin_id, self._build_message(msg_type, payload))

    def _send_request(
        self,
        target_twin_id: str,
        msg_type: str,
        payload: Any,
    ) -> asyncio.Future[TwinMessageResult]:
        """Send request and wait for response."""
        request_id = self._generate_request_id()
        loop = self._get_loop()
        future: asyncio.Future[TwinMessageResult] = loop.create_future()

        def on_timeout() -> None:
            if request_id in self._pending_requests:
                del self._pending_requests[request_id]
                if not future.done():
                    future.set_exception(
                        TimeoutError(f"Request timed out after {REQUEST_TIMEOUT}s")
                    )

        timeout_handle = loop.call_later(REQUEST_TIMEOUT, on_timeout)
        self._pending_requests[request_id] = PendingRequest(
            future=future,
            timeout_handle=timeout_handle,
        )

        # Send with requestId embedded
        request_payload = {**(payload or {}), "requestId": request_id}
        self._context.send_event(
            target_twin_id,
            self._build_message(msg_type, request_payload),
        )

        return future

    def _setup_response_listener(self) -> None:
        """Set up response listener for request-response pattern."""

        def handle_response(payload: dict[str, Any]) -> None:
            message_type = (payload.get("data") or {}).get("type") or payload.get("type")
            if message_type == f"{self._context.type_prefix}:response":
                response_data = (payload.get("data") or {}).get("data") or payload.get("data")
                request_id = (response_data or {}).get("requestId")

                pending = self._pending_requests.get(request_id)
                if pending:
                    if pending.timeout_handle:
                        pending.timeout_handle.cancel()
                    del self._pending_requests[request_id]

                    # Extract result without requestId
                    result_data = {k: v for k, v in (response_data or {}).items() if k != "requestId"}
                    result = TwinMessageResult(
                        status=TwinMessageResultStatus(result_data.get("status", "success")),
                        message=result_data.get("message", ""),
                        data=result_data.get("data"),
                    )

                    if not pending.future.done():
                        pending.future.set_result(result)

        self._context.on_twin_message(self._context.twin_id, handle_response)

    def emit(self, event_type: str, payload: Any = None) -> None:
        """Fire-and-forget broadcast to subscribers.

        Args:
            event_type: Type of event to emit.
            payload: Data to send.
        """
        self._send_message(self._context.twin_id, event_type, payload)

    def on(
        self,
        event_type: str,
        callback: Callable[[Any, Optional[Callable[[TwinMessageResult], None]]], None],
    ) -> None:
        """Listen for events, with optional respond callback for request-response.

        Args:
            event_type: Type of event to listen for.
            callback: Handler function (data, respond?) => None
        """
        expected_type = f"{self._context.type_prefix}:{event_type}"

        def handler(payload: dict[str, Any]) -> None:
            message_type = (payload.get("data") or {}).get("type") or payload.get("type")

            if message_type == expected_type:
                message_data = (payload.get("data") or {}).get("data") or payload.get("data")
                request_id = (message_data or {}).get("requestId") if message_data else None
                source_twin_id = payload.get("sourceTwinId")

                # Create respond callback if this is a request
                respond: Optional[Callable[[TwinMessageResult], None]] = None
                if request_id and source_twin_id:

                    def respond_fn(result: TwinMessageResult) -> None:
                        response_data = {
                            "status": result.status.value,
                            "message": result.message,
                            "requestId": request_id,
                        }
                        if result.data:
                            response_data["data"] = result.data
                        self._context.send_event(
                            source_twin_id,
                            self._build_message("response", response_data),
                        )

                    respond = respond_fn

                # Strip requestId from payload
                if message_data and isinstance(message_data, dict):
                    clean_data = {k: v for k, v in message_data.items() if k != "requestId"}
                else:
                    clean_data = message_data

                callback(clean_data, respond)

        self._context.on_twin_message(self._context.twin_id, handler)

    def to(self, target_twin_id: str) -> TargetedEmitter:
        """Target a specific twin for messaging.

        Args:
            target_twin_id: ID of twin to target.

        Returns:
            TargetedEmitter for the specified twin.
        """
        return TargetedEmitter(
            target_twin_id=target_twin_id,
            send_message=self._send_message,
            send_request=self._send_request,
        )


def create_twin_messaging(context: TwinMessagingContext) -> TwinMessaging:
    """Create messaging methods (emit, on, to) for a twin instance.

    Args:
        context: Configuration context.

    Returns:
        TwinMessaging instance.
    """
    return TwinMessaging(context)
