# grpctunnel-py: Client Cancellation Handling Improvements

## Executive Summary

The `grpctunnel-py` library currently suffers from unhandled `asyncio.InvalidStateError: RPC already finished` exceptions when clients cancel requests. This analysis identifies the root cause and proposes several solutions with varying trade-offs.

---

## Root Cause Analysis

### The Race Condition

```
Timeline of Events:
T1: Client sends RPC request through tunnel
T2: Worker begins processing (handler running)
T3: Client cancels HTTP request (tab switch, navigation, timeout)
T4: Underlying gRPC bidirectional stream closes immediately
T5: Worker completes processing successfully
T6: Worker tries to send response → InvalidStateError (stream already closed)
T7: _finish_stream() tries to send close message → InvalidStateError again
```

### Code Locations

**Error 1: Sending response (server.py:514)**
```python
async def _serve_stream(self) -> None:
    try:
        response = await self._handler(request, self._context)
        await self.send_message(response)  # ← Stream already closed!
    finally:
        await self._finish_stream(err)
```

**Error 2: Sending headers (server.py:705)**
```python
async def _send_headers_locked(self) -> None:
    headers_proto = to_proto(self._response_headers)
    msg = ServerToClient(...)
    await self._tunnel_stream.write(msg)  # ← Stream already closed!
```

**Error 3: Sending close message (server.py:771)**
```python
async def send_close() -> None:
    close_msg = ServerToClient(...)
    await self._tunnel_stream.write(close_msg)  # ← Stream already closed!

asyncio.create_task(send_close())  # Fire-and-forget, no error handling
```

### Why This Happens

1. **No stream state checking**: Code never checks if `_tunnel_stream` is still active before writing
2. **Fire-and-forget cleanup**: `send_close()` launched as unmonitored task (line 773)
3. **Synchronous handlers**: Handler completes successfully, unaware client disconnected
4. **Silent cancellation**: HTTP cancellation doesn't send explicit cancel frame, just closes stream

---

## Proposed Solutions

### Solution 1: Defensive Write Wrapper (Recommended)

**Approach**: Wrap all writes to `_tunnel_stream` with try/except to gracefully handle closed streams.

**Implementation**:

```python
class TunnelServerStream:
    def __init__(self, ...):
        # ... existing initialization ...
        self._tunnel_stream_closed = False  # Track stream state

    async def _safe_tunnel_write(
        self,
        msg: ServerToClient,
        operation: str = "write"
    ) -> bool:
        """
        Safely write to tunnel stream, handling closed stream gracefully.

        Args:
            msg: Message to write
            operation: Description of operation (for logging)

        Returns:
            True if write succeeded, False if stream already closed
        """
        if self._tunnel_stream_closed:
            # Already know stream is closed, skip write
            return False

        try:
            await self._tunnel_stream.write(msg)
            return True
        except asyncio.InvalidStateError as e:
            # Stream was closed by client (cancellation or timeout)
            self._tunnel_stream_closed = True
            # Log at debug level - this is expected behavior
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(
                f"Stream {self._stream_id} ({self._method_name}): "
                f"Cannot {operation}, client closed connection"
            )
            return False
        except Exception as e:
            # Unexpected error, log at error level
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Stream {self._stream_id} ({self._method_name}): "
                f"Unexpected error during {operation}: {e}"
            )
            self._tunnel_stream_closed = True
            return False

    async def _send_headers_locked(self) -> None:
        """Send response headers (must hold write lock)."""
        if self._sent_headers:
            return

        headers_proto = to_proto(self._response_headers)
        msg = ServerToClient(
            stream_id=self._stream_id,
            response_headers=headers_proto,
        )

        # Use safe write instead of direct write
        success = await self._safe_tunnel_write(msg, "send headers")
        if success:
            self._sent_headers = True
            self._response_headers = None
        # If write failed, stream is closed anyway, just mark as sent to prevent retries
        else:
            self._sent_headers = True
            self._response_headers = None

    async def _finish_stream(self, err: Optional[Exception]) -> None:
        """Finish the stream and send close message to client."""
        await self._half_close(err)
        await self._server._remove_stream(self._stream_id)

        async with self._write_lock:
            if self._closed:
                return

            self._closed = True
            status = _error_to_status(err)

            # Prepare messages
            send_headers = not self._sent_headers
            headers = self._response_headers if send_headers else None
            trailers = self._response_trailers

            # Send close message with proper error handling
            async def send_close() -> None:
                try:
                    if send_headers and headers is not None:
                        headers_msg = ServerToClient(
                            stream_id=self._stream_id,
                            response_headers=to_proto(headers),
                        )
                        await self._safe_tunnel_write(headers_msg, "send final headers")

                    close_msg = ServerToClient(
                        stream_id=self._stream_id,
                        close_stream={
                            "status": status,
                            "response_trailers": to_proto(trailers),
                        },
                    )
                    await self._safe_tunnel_write(close_msg, "send close")
                except Exception as e:
                    # Log unexpected errors in cleanup
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(
                        f"Stream {self._stream_id}: Error in cleanup: {e}"
                    )

            # Still fire-and-forget, but now with internal error handling
            asyncio.create_task(send_close())

            self._sent_headers = True
            self._response_headers = None
            self._response_trailers = None
```

**Pros**:
- ✅ Minimal changes to existing API
- ✅ Gracefully handles all cancellation scenarios
- ✅ Preserves existing behavior for successful paths
- ✅ Appropriate logging levels (debug for expected, error for unexpected)

**Cons**:
- ⚠️ Slight overhead of try/except on every write
- ⚠️ Doesn't prevent handler from executing after cancellation

---

### Solution 2: Proactive Stream Monitoring

**Approach**: Monitor the underlying gRPC stream and set a cancellation flag when it closes.

**Implementation**:

```python
class TunnelServerStream:
    def __init__(self, ...):
        # ... existing initialization ...
        self._cancellation_event = asyncio.Event()
        self._monitor_task = asyncio.create_task(self._monitor_tunnel_stream())

    async def _monitor_tunnel_stream(self) -> None:
        """Monitor the tunnel stream for premature closure."""
        try:
            # Wait for the stream to complete
            await self._tunnel_stream.done()

            # If we reach here, stream closed (either normally or via cancellation)
            # Check if our stream is still processing
            if not self._closed:
                # Stream closed while we were still processing
                self._cancellation_event.set()
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(
                    f"Stream {self._stream_id} ({self._method_name}): "
                    f"Client disconnected during processing"
                )
        except Exception as e:
            # Shouldn't happen, but log just in case
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Stream monitor error: {e}")

    async def _safe_tunnel_write(self, msg: ServerToClient, operation: str = "write") -> bool:
        """Write to tunnel stream, respecting cancellation."""
        if self._cancellation_event.is_set():
            # Client already disconnected
            return False

        try:
            await self._tunnel_stream.write(msg)
            return True
        except asyncio.InvalidStateError:
            self._cancellation_event.set()
            return False

    async def _serve_stream(self) -> None:
        """Serve this stream by invoking the handler."""
        err: Optional[Exception] = None

        try:
            # For long-running handlers, could check cancellation periodically
            response = await self._handler(request, self._context)

            # Check if cancelled before sending response
            if self._cancellation_event.is_set():
                # Client disconnected, don't bother sending
                err = Exception("client disconnected")
            else:
                await self.send_message(response)

        except Exception as e:
            err = e

        finally:
            await self._finish_stream(err)

            # Clean up monitor task
            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
```

**Pros**:
- ✅ Proactive detection of client disconnection
- ✅ Can abort handler execution if needed
- ✅ Clean separation of concerns

**Cons**:
- ⚠️ Requires `done()` method on gRPC stream (may not exist in all versions)
- ⚠️ Additional background task per stream
- ⚠️ More complex state management

---

### Solution 3: Context-Based Cancellation

**Approach**: Expose cancellation state to handler through context.

**Implementation**:

```python
class _ServerContext:
    """Context object passed to server handlers."""

    def __init__(self, stream: TunnelServerStream):
        self._stream = stream

    def is_active(self) -> bool:
        """Check if the client is still connected."""
        return not self._stream._cancellation_event.is_set()

    async def wait_for_cancellation(self) -> None:
        """Wait until client disconnects."""
        await self._stream._cancellation_event.wait()

# Handlers can now check cancellation:
async def long_running_handler(request, context):
    for i in range(1000):
        if not context.is_active():
            # Client disconnected, abort processing
            raise Exception("client disconnected")

        # Do work...
        await asyncio.sleep(0.1)

    return response
```

**Pros**:
- ✅ Handlers can be cancellation-aware
- ✅ Prevents wasted computation
- ✅ Most flexible solution

**Cons**:
- ⚠️ Requires handler modifications
- ⚠️ Breaking API change (adds new context methods)
- ⚠️ Handlers must opt-in to cancellation checking

---

### Solution 4: Combined Approach (Most Robust)

Combine Solutions 1 and 2 for defense-in-depth:

```python
class TunnelServerStream:
    def __init__(self, ...):
        self._tunnel_stream_closed = False
        self._cancellation_event = asyncio.Event()
        # Don't start monitor if stream doesn't support done()
        if hasattr(self._tunnel_stream, 'done'):
            self._monitor_task = asyncio.create_task(self._monitor_tunnel_stream())
        else:
            self._monitor_task = None

    async def _monitor_tunnel_stream(self) -> None:
        """Proactively detect stream closure."""
        try:
            await self._tunnel_stream.done()
            if not self._closed:
                self._cancellation_event.set()
                self._tunnel_stream_closed = True
        except Exception:
            pass

    async def _safe_tunnel_write(self, msg: ServerToClient, operation: str = "write") -> bool:
        """Defensive write with fallback."""
        if self._tunnel_stream_closed or self._cancellation_event.is_set():
            return False

        try:
            await self._tunnel_stream.write(msg)
            return True
        except asyncio.InvalidStateError:
            self._tunnel_stream_closed = True
            self._cancellation_event.set()
            return False
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Unexpected write error: {e}")
            self._tunnel_stream_closed = True
            return False
```

**Pros**:
- ✅ Multiple layers of protection
- ✅ Works even if `done()` not available
- ✅ Minimal performance impact

**Cons**:
- ⚠️ Slightly more complex implementation

---

## Recommendation

**Implement Solution 4 (Combined Approach)**:
1. Add `_safe_tunnel_write()` wrapper (Solution 1)
2. Add optional stream monitoring if `done()` available (Solution 2)
3. Expose `is_active()` in context for opt-in handler cancellation (Solution 3)

This provides:
- **Immediate fix** for the error spam (defensive writes)
- **Proactive detection** when possible (monitoring)
- **Handler flexibility** for long-running operations (context methods)
- **Backward compatibility** (no breaking changes)

---

## Additional Improvements

### 1. Logging Configuration

Add module-level logger with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

# In _safe_tunnel_write:
logger.debug(  # DEBUG for expected client cancellations
    f"Stream {self._stream_id}: Client disconnected during {operation}"
)
```

### 2. Metrics/Observability

Add optional callback for cancellation events:

```python
class TunnelServerStream:
    def __init__(self, ..., on_client_disconnect: Optional[Callable] = None):
        self._on_client_disconnect = on_client_disconnect

    async def _safe_tunnel_write(self, ...):
        try:
            await self._tunnel_stream.write(msg)
        except asyncio.InvalidStateError:
            if self._on_client_disconnect:
                self._on_client_disconnect(self._stream_id, self._method_name)
```

### 3. Testing

Add integration test for cancellation scenarios:

```python
async def test_client_cancellation_during_processing():
    """Test that server handles client cancellation gracefully."""
    # Start RPC
    call = stub.SlowMethod(request)

    # Cancel after handler starts but before it completes
    await asyncio.sleep(0.1)
    call.cancel()

    # Server should handle gracefully without errors
    # (Check server logs for no InvalidStateError)
```

---

## Migration Path

**Phase 1** (Immediate):
- Implement `_safe_tunnel_write()` wrapper
- Replace all `_tunnel_stream.write()` calls
- Add `_tunnel_stream_closed` flag

**Phase 2** (Next minor version):
- Add optional stream monitoring
- Expose `is_active()` in context
- Add metrics callbacks

**Phase 3** (Next major version):
- Make context cancellation checking the default
- Add helper decorators for cancellation-aware handlers

---

## Impact Assessment

**Before Fix**:
- 6-12 exceptions per background process per scroll/tab switch
- Noisy logs masking real errors
- Potential memory leaks from unhandled async tasks

**After Fix**:
- Zero exceptions for client cancellations
- Clean debug-level logging for expected cancellations
- Graceful degradation
- Optional early handler termination

---

## References

- Original Go implementation: https://github.com/jhump/grpctunnel
- Python gRPC AsyncIO API: https://grpc.github.io/grpc/python/grpc_asyncio.html
- Related issue: Race condition in grpctunnel cleanup code
