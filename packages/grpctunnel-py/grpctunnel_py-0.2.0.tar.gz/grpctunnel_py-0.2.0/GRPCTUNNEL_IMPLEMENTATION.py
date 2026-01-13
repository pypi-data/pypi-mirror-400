"""
Reference implementation for grpctunnel-py cancellation handling improvements.

This file shows the exact changes needed to implement Solution 4 (Combined Approach)
from GRPCTUNNEL_CANCELLATION_FIX.md.

Apply these changes to: src/grpctunnel/server.py
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TunnelServerStream:
    """
    Server-side implementation of a single tunneled stream.

    CHANGES FROM ORIGINAL:
    - Added _tunnel_stream_closed flag
    - Added _cancellation_event for proactive detection
    - Added _monitor_task for stream monitoring
    - Added _safe_tunnel_write() wrapper
    - Modified _send_headers_locked() to use safe write
    - Modified _finish_stream() to use safe write
    - Added cleanup for monitor task
    """

    def __init__(
        self,
        server,
        tunnel_stream,
        stream_id: int,
        method_name: str,
        sender,
        receiver,
        handler,
        is_client_stream: bool,
        is_server_stream: bool,
        headers,
    ):
        self._server = server
        self._tunnel_stream = tunnel_stream
        self._stream_id = stream_id
        self._method_name = method_name
        self._sender = sender
        self._receiver = receiver
        self._handler = handler
        self._is_client_stream = is_client_stream
        self._is_server_stream = is_server_stream

        # Metadata
        self._request_headers = headers
        self._response_headers: Optional[grpc.aio.Metadata] = None
        self._response_trailers: Optional[grpc.aio.Metadata] = None

        # State
        self._sent_headers = False
        self._closed = False
        self._half_closed_err: Optional[Exception] = None
        self._num_sent = 0
        self._read_err: Optional[Exception] = None

        # NEW: Cancellation tracking
        self._tunnel_stream_closed = False
        self._cancellation_event = asyncio.Event()

        # Locks
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()

        # Context for handler
        self._context = _ServerContext(self)

        # NEW: Start stream monitor if done() method available
        # (gRPC AsyncIO streams have done() method in newer versions)
        if hasattr(self._tunnel_stream, 'done') and callable(getattr(self._tunnel_stream, 'done')):
            self._monitor_task = asyncio.create_task(self._monitor_tunnel_stream())
        else:
            self._monitor_task = None
            logger.debug(
                f"Stream monitoring not available for stream {stream_id} "
                "(gRPC stream doesn't support done() method)"
            )

    # NEW METHOD
    async def _monitor_tunnel_stream(self) -> None:
        """
        Monitor the tunnel stream for premature closure.

        This runs as a background task and sets the cancellation event
        if the underlying gRPC stream closes while we're still processing.
        """
        try:
            # Wait for the underlying gRPC stream to complete
            await self._tunnel_stream.done()

            # If we reach here, the stream has closed
            # Check if our tunnel stream is still processing
            if not self._closed:
                # Stream closed prematurely (client cancellation)
                self._cancellation_event.set()
                self._tunnel_stream_closed = True
                logger.debug(
                    f"Stream {self._stream_id} ({self._method_name}): "
                    f"Detected client disconnection"
                )
        except Exception as e:
            # Shouldn't normally happen, but log defensively
            logger.debug(
                f"Stream {self._stream_id}: Monitor task error: {e}",
                exc_info=True
            )

    # NEW METHOD
    async def _safe_tunnel_write(
        self,
        msg,  # ServerToClient message
        operation: str = "write"
    ) -> bool:
        """
        Safely write to tunnel stream, handling closed streams gracefully.

        This wrapper provides defense-in-depth:
        1. Check cancellation flag (set by monitor or previous write failure)
        2. Attempt write with try/except
        3. Catch InvalidStateError and update flags
        4. Log at appropriate level

        Args:
            msg: ServerToClient message to write
            operation: Human-readable description for logging

        Returns:
            True if write succeeded, False if stream already closed
        """
        # Fast path: Already know stream is closed
        if self._tunnel_stream_closed or self._cancellation_event.is_set():
            logger.debug(
                f"Stream {self._stream_id} ({self._method_name}): "
                f"Skipping {operation}, client already disconnected"
            )
            return False

        try:
            await self._tunnel_stream.write(msg)
            return True

        except asyncio.InvalidStateError as e:
            # Expected: Client cancelled/disconnected
            # This is normal operation, log at DEBUG level
            self._tunnel_stream_closed = True
            self._cancellation_event.set()
            logger.debug(
                f"Stream {self._stream_id} ({self._method_name}): "
                f"Cannot {operation}, client closed connection: {e}"
            )
            return False

        except Exception as e:
            # Unexpected error - log at ERROR level
            self._tunnel_stream_closed = True
            self._cancellation_event.set()
            logger.error(
                f"Stream {self._stream_id} ({self._method_name}): "
                f"Unexpected error during {operation}: {e}",
                exc_info=True
            )
            return False

    # MODIFIED METHOD
    async def _send_headers_locked(self) -> None:
        """
        Send response headers (must hold write lock).

        CHANGE: Uses _safe_tunnel_write() instead of direct write.
        """
        if self._sent_headers:
            return

        headers_proto = to_proto(self._response_headers)
        msg = ServerToClient(
            stream_id=self._stream_id,
            response_headers=headers_proto,
        )

        # OLD: await self._tunnel_stream.write(msg)
        # NEW: Use safe write wrapper
        success = await self._safe_tunnel_write(msg, "send response headers")

        # Always mark as sent to prevent retries
        # (If write failed, stream is closed anyway)
        self._sent_headers = True
        self._response_headers = None

        if not success:
            logger.debug(
                f"Stream {self._stream_id}: Failed to send headers "
                "(client disconnected)"
            )

    # MODIFIED METHOD
    async def _finish_stream(self, err: Optional[Exception]) -> None:
        """
        Finish the stream and send close message to client.

        CHANGES:
        - Uses _safe_tunnel_write() for headers and close message
        - Adds error handling to send_close() task
        - Cleans up monitor task
        """
        # Mark as half-closed
        await self._half_close(err)

        # Remove from server's stream map
        await self._server._remove_stream(self._stream_id)

        async with self._write_lock:
            if self._closed:
                return

            self._closed = True

            # Convert error to status
            status = _error_to_status(err)

            # Prepare headers and trailers
            send_headers = not self._sent_headers
            headers = self._response_headers if send_headers else None
            trailers = self._response_trailers

            # Send close message (don't block)
            async def send_close() -> None:
                """Send final headers and close message with error handling."""
                try:
                    # Send final headers if not already sent
                    if send_headers and headers is not None:
                        headers_msg = ServerToClient(
                            stream_id=self._stream_id,
                            response_headers=to_proto(headers),
                        )
                        await self._safe_tunnel_write(
                            headers_msg,
                            "send final headers"
                        )

                    # Send close message
                    close_msg = ServerToClient(
                        stream_id=self._stream_id,
                        close_stream={
                            "status": status,
                            "response_trailers": to_proto(trailers),
                        },
                    )
                    await self._safe_tunnel_write(close_msg, "send close")

                except Exception as e:
                    # Catch any unexpected errors in cleanup
                    # (should be rare since _safe_tunnel_write handles most errors)
                    logger.debug(
                        f"Stream {self._stream_id}: Error in close cleanup: {e}",
                        exc_info=True
                    )

                finally:
                    # NEW: Clean up monitor task if it exists
                    if self._monitor_task and not self._monitor_task.done():
                        self._monitor_task.cancel()
                        try:
                            await self._monitor_task
                        except asyncio.CancelledError:
                            pass

            # Fire-and-forget with error handling
            asyncio.create_task(send_close())

            # Clear state
            self._sent_headers = True
            self._response_headers = None
            self._response_trailers = None

    # EXISTING METHOD - no changes needed, but shown for context
    async def send_message(
        self,
        message,
        serializer=None,
    ) -> None:
        """
        Send a message to the client.

        NOTE: This method already acquires _write_lock and calls
        _send_headers_locked(), which now uses safe writes.
        No changes needed here.
        """
        async with self._write_lock:
            # Send headers if not already sent
            if not self._sent_headers:
                await self._send_headers_locked()  # Now uses safe write

            # Check if we're allowed to send another message
            if not self._is_server_stream and self._num_sent >= 1:
                raise grpc.aio.AioRpcError(...)

            self._num_sent += 1

            # Serialize and send message
            if serializer:
                data = serializer(message)
            elif isinstance(message, ProtoMessage):
                data = message.SerializeToString()
            else:
                data = message

            await self._sender.send(data)  # Uses flow control, separate path


class _ServerContext:
    """
    Context object passed to server handlers.

    CHANGES:
    - Added is_active() method for cancellation checking
    - Added wait_for_cancellation() for async cancellation detection
    """

    def __init__(self, stream: TunnelServerStream):
        self._stream = stream

    def invocation_metadata(self):
        """Get the request headers metadata."""
        return self._stream._request_headers

    # NEW METHOD
    def is_active(self) -> bool:
        """
        Check if the client connection is still active.

        Returns:
            True if client is connected, False if disconnected/cancelled

        Example:
            async def long_handler(request, context):
                for i in range(1000):
                    if not context.is_active():
                        raise Exception("client disconnected")
                    await process_item(i)
                return response
        """
        return not self._stream._cancellation_event.is_set()

    # NEW METHOD
    async def wait_for_cancellation(self) -> None:
        """
        Wait until the client disconnects.

        This can be used with asyncio.wait() to race handler execution
        against client disconnection:

        Example:
            async def handler(request, context):
                work_task = asyncio.create_task(do_work())
                cancel_task = asyncio.create_task(context.wait_for_cancellation())

                done, pending = await asyncio.wait(
                    {work_task, cancel_task},
                    return_when=asyncio.FIRST_COMPLETED
                )

                if cancel_task in done:
                    work_task.cancel()
                    raise Exception("client disconnected")

                return await work_task
        """
        await self._stream._cancellation_event.wait()


# USAGE EXAMPLE: Cancellation-aware handler
async def example_long_running_handler(request, context):
    """
    Example handler that checks for client cancellation.

    This is OPTIONAL - handlers don't need to check cancellation
    unless they do expensive long-running work.
    """
    result = []

    for i in range(1000):
        # Periodically check if client is still connected
        if not context.is_active():
            logger.info("Client disconnected, aborting processing")
            raise Exception("client disconnected")

        # Do expensive work
        item = await process_expensive_item(i)
        result.append(item)

        # Optional: yield control to event loop
        if i % 100 == 0:
            await asyncio.sleep(0)

    return MyResponse(items=result)


# MIGRATION NOTES:
#
# 1. Add to __init__:
#    - self._tunnel_stream_closed = False
#    - self._cancellation_event = asyncio.Event()
#    - self._monitor_task = ... (conditional)
#
# 2. Add new method: _monitor_tunnel_stream()
#
# 3. Add new method: _safe_tunnel_write()
#
# 4. Modify _send_headers_locked():
#    - Replace direct write with _safe_tunnel_write()
#
# 5. Modify _finish_stream():
#    - Replace direct writes with _safe_tunnel_write()
#    - Add try/except to send_close()
#    - Add monitor_task cleanup
#
# 6. Add to _ServerContext:
#    - is_active() method
#    - wait_for_cancellation() method
#
# 7. Update tests:
#    - Add test_client_cancellation_during_processing()
#    - Add test_cancellation_aware_handler()
#
# 8. Update documentation:
#    - Document new context methods
#    - Add examples of cancellation-aware handlers
