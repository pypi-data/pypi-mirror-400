# Copyright 2024 Daniel Valdivia
# Ported from the original Go implementation by Joshua Humphries
# Original: https://github.com/jhump/grpctunnel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tunnel server implementation.

This module provides the server-side implementation of the gRPC tunnel protocol,
allowing a server to accept tunnel connections and dispatch RPCs to registered
service handlers.

Based on the Go implementation by Joshua Humphries:
https://github.com/jhump/grpctunnel
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import grpc
from grpc import aio
from google.protobuf.message import Message as ProtoMessage
from google.rpc import status_pb2

from grpctunnel.flow_control import (
    Receiver,
    Sender,
    new_receiver,
    new_receiver_without_flow_control,
    new_sender,
    new_sender_without_flow_control,
)
from grpctunnel.metadata import from_proto, to_proto
from grpctunnel.options import TunnelOptions
from grpctunnel.proto.v1 import (
    REVISION_ONE,
    REVISION_ZERO,
    ClientToServer,
    ServerToClient,
)

# Initial window size for flow control (64KB)
INITIAL_WINDOW_SIZE = 65536

# Logger for this module
logger = logging.getLogger(__name__)


@dataclass
class MethodHandler:
    """Handler for a registered RPC method."""

    handler: Callable[..., Any]
    """The async handler function that implements the method."""

    is_client_stream: bool = False
    """Whether this is a client streaming method."""

    is_server_stream: bool = False
    """Whether this is a server streaming method."""


class TunnelServer:
    """
    Server-side implementation of the gRPC tunnel protocol.

    The TunnelServer accepts incoming tunnel connections and dispatches RPCs
    to registered service handlers. Each tunnel connection can multiplex many
    concurrent RPCs.

    Example usage:
        server = TunnelServer()
        server.register_method("myservice.MyService/MyMethod", my_handler)
        await server.serve_tunnel(stream)
    """

    def __init__(
        self,
        options: Optional[TunnelOptions] = None,
        interceptors: Optional[Sequence[aio.ServerInterceptor]] = None,
    ):
        """
        Initialize a new TunnelServer.

        Args:
            options: Optional tunnel configuration. If None, uses default options.
            interceptors: Optional sequence of server interceptors to apply.
        """
        self._options = options or TunnelOptions()
        self._interceptors = list(interceptors) if interceptors else []
        self._handlers: Dict[str, MethodHandler] = {}
        self._streams: Dict[int, "TunnelServerStream"] = {}
        self._last_seen = -1
        self._stream_lock = asyncio.Lock()
        self._is_closing = False
        # Write queue to serialize all writes through the main loop
        # This prevents concurrent read/write operations on the gRPC stream
        self._write_queue: asyncio.Queue[ServerToClient] = asyncio.Queue()

    def register_method(
        self,
        method_name: str,
        handler: Callable[..., Any],
        is_client_stream: bool = False,
        is_server_stream: bool = False,
    ) -> None:
        """
        Register a method handler.

        Args:
            method_name: Full method name like "myservice.MyService/MyMethod"
            handler: Async callable that implements the method.
                     For unary methods: async def handler(request, context) -> response
                     For streaming methods: async def handler(stream) -> None
            is_client_stream: Whether this is a client streaming method
            is_server_stream: Whether this is a server streaming method
        """
        # Apply interceptors if any
        if self._interceptors:
            handler = self._wrap_handler_with_interceptors(
                method_name, handler, is_client_stream, is_server_stream
            )

        self._handlers[method_name] = MethodHandler(
            handler=handler,
            is_client_stream=is_client_stream,
            is_server_stream=is_server_stream,
        )

    def _wrap_handler_with_interceptors(
        self,
        method_name: str,
        handler: Callable[..., Any],
        is_client_stream: bool,
        is_server_stream: bool,
    ) -> Callable[..., Any]:
        """
        Wrap a handler with interceptors.

        Args:
            method_name: Full method name
            handler: The original handler
            is_client_stream: Whether this is a client streaming method
            is_server_stream: Whether this is a server streaming method

        Returns:
            A wrapped handler that applies the interceptor chain
        """
        # Create handler call details
        class HandlerCallDetails:
            def __init__(self, method: str):
                self.method = method
                self.invocation_metadata = None

        call_details = HandlerCallDetails(method=method_name)

        # Build continuation chain from interceptors
        def build_continuation(index: int) -> Callable:
            """Build the continuation chain recursively."""
            if index >= len(self._interceptors):
                # Base case: return the original handler
                return lambda _: handler

            # Get next continuation
            next_continuation = build_continuation(index + 1)
            interceptor = self._interceptors[index]

            # Create continuation that invokes interceptor
            def continuation(details: Any) -> Callable:
                # Invoke the interceptor's intercept_service method
                try:
                    return interceptor.intercept_service(next_continuation, details)
                except AttributeError:
                    # If interceptor doesn't have intercept_service, skip it
                    return next_continuation(details)

            return continuation

        # Apply the interceptor chain
        continuation = build_continuation(0)
        wrapped_handler = continuation(call_details)

        # If we got back a valid handler, use it; otherwise use original
        return wrapped_handler if wrapped_handler is not None else handler

    def shutdown(self) -> None:
        """Mark the server as shutting down."""
        self._is_closing = True

    async def enqueue_write(self, msg: ServerToClient) -> None:
        """
        Enqueue a message to be written to the tunnel stream.

        This method is safe to call from any coroutine. The message will be
        written by the main serve_tunnel loop, ensuring no concurrent
        read/write operations on the gRPC stream.
        """
        await self._write_queue.put(msg)

    async def serve_tunnel(
        self,
        stream: grpc.aio.StreamStreamCall[ClientToServer, ServerToClient],
        client_accepts_settings: bool = True,
    ) -> None:
        """
        Serve a tunnel connection.

        This method handles an incoming OpenTunnel RPC stream, negotiates settings
        with the client, and dispatches incoming RPCs to registered handlers.

        Args:
            stream: The bidirectional gRPC stream for the tunnel
            client_accepts_settings: Whether the client accepts settings negotiation
        """
        # Send settings if client accepts them
        if client_accepts_settings:
            settings_msg = ServerToClient(
                stream_id=-1,
                settings={
                    "initial_window_size": INITIAL_WINDOW_SIZE,
                    "supported_protocol_revisions": self._options.supported_revisions(),
                },
            )
            # Send settings and wait for it to be written
            await stream.write(settings_msg)

        # Main receive loop - uses a persistent read task to avoid cancellation issues
        # Writes are processed when read completes or when signaled via write_event
        read_task: Optional[asyncio.Task] = None
        write_wait_task: Optional[asyncio.Task] = None
        write_event = asyncio.Event()

        # Patch enqueue_write to signal when writes are available
        original_enqueue = self.enqueue_write
        async def signaling_enqueue(msg: ServerToClient) -> None:
            await original_enqueue(msg)
            write_event.set()
        self.enqueue_write = signaling_enqueue  # type: ignore

        try:
            while not self._is_closing:
                # Start a read task if we don't have one
                if read_task is None:
                    read_coro = stream.read() if hasattr(stream, 'read') else stream.__anext__()
                    read_task = asyncio.create_task(read_coro)

                # Wait for either read to complete or writes to be available
                write_wait_task = asyncio.create_task(write_event.wait())
                try:
                    done, _ = await asyncio.wait(
                        [read_task, write_wait_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                finally:
                    # Always cancel the write_wait_task if still pending
                    if not write_wait_task.done():
                        write_wait_task.cancel()
                        try:
                            await write_wait_task
                        except asyncio.CancelledError:
                            pass
                    write_wait_task = None

                # Process any pending writes (non-blocking)
                if write_event.is_set():
                    write_event.clear()
                    while not self._write_queue.empty():
                        try:
                            write_msg = self._write_queue.get_nowait()
                            await stream.write(write_msg)
                        except asyncio.QueueEmpty:
                            break

                # Process read result if available
                if read_task in done:
                    try:
                        msg = read_task.result()
                    except Exception:
                        # Read failed, exit loop
                        break
                    finally:
                        read_task = None  # Will start new read on next iteration

                    if msg is None:
                        # Stream is closing or no more messages
                        async with self._stream_lock:
                            num_streams = len(self._streams)
                        if num_streams == 0:
                            break
                        continue

                    # Handle NewStream messages - create new stream
                    if msg.HasField("new_stream"):
                        ok, err = await self._create_stream(stream, msg.stream_id, msg.new_stream)
                        if not ok:
                            raise Exception(f"Protocol error: {err}")
                        if err is not None:
                            close_msg = ServerToClient(
                                stream_id=msg.stream_id,
                                close_stream={
                                    "status": _error_to_status(err),
                                },
                            )
                            await self.enqueue_write(close_msg)
                        continue

                    # Route message to appropriate stream
                    target_stream = await self._get_stream(msg.stream_id)
                    if target_stream is not None:
                        await target_stream._accept_client_frame(msg)

        except asyncio.CancelledError:
            # Don't try to write to stream on cancellation - it may be closed
            # Just discard any pending writes
            while not self._write_queue.empty():
                try:
                    self._write_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            raise  # Re-raise CancelledError to signal cancellation
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Clean up pending tasks
            if read_task is not None and not read_task.done():
                read_task.cancel()
                try:
                    await read_task
                except asyncio.CancelledError:
                    pass
            # Restore original enqueue_write
            self.enqueue_write = original_enqueue  # type: ignore

    async def _create_stream(
        self,
        tunnel_stream: grpc.aio.StreamStreamCall[ClientToServer, ServerToClient],
        stream_id: int,
        new_stream_msg: Any,
    ) -> tuple[bool, Optional[Exception]]:
        """
        Create a new stream with the given ID.

        Returns:
            (ok, err) tuple where:
            - ok=False means protocol error, tunnel should be aborted
            - ok=True, err=None means stream created successfully
            - ok=True, err=Exception means stream should be closed with error
        """
        if self._is_closing:
            return True, grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNAVAILABLE,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details="server is shutting down",
            )

        # Validate protocol revision
        revision = new_stream_msg.protocol_revision
        if revision not in (REVISION_ZERO, REVISION_ONE):
            return True, grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNAVAILABLE,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details=f"server does not support protocol revision {revision}",
            )

        no_flow_control = revision == REVISION_ZERO

        async with self._stream_lock:
            # Check for duplicate stream ID
            if stream_id in self._streams:
                return False, Exception(
                    f"cannot create stream ID {stream_id}: already exists"
                )

            # Check for monotonic stream IDs
            if stream_id <= self._last_seen:
                return False, Exception(
                    f"cannot create stream ID {stream_id}: that ID has already been used"
                )

            self._last_seen = stream_id

            # Parse method name
            method_name = new_stream_msg.method_name
            if method_name.startswith("/"):
                method_name = method_name[1:]

            # Look up handler
            handler_info = self._handlers.get(method_name)
            if handler_info is None:
                return True, grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNIMPLEMENTED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"{method_name} not implemented",
                )

            # Parse request headers metadata
            headers = from_proto(new_stream_msg.request_headers)

            # Create sender for this stream - uses enqueue_write to avoid concurrent ops
            async def send_func(data: bytes, total_size: int, first: bool) -> None:
                if first:
                    msg = ServerToClient(
                        stream_id=stream_id,
                        response_message={"size": total_size, "data": data},
                    )
                else:
                    msg = ServerToClient(
                        stream_id=stream_id,
                        more_response_data=data,
                    )
                await self.enqueue_write(msg)

            # Create sender and receiver based on protocol revision
            if no_flow_control:
                sender = new_sender_without_flow_control(send_func)
                receiver: Receiver[Any] = new_receiver_without_flow_control()
            else:

                def send_window_update(window: int) -> None:
                    # Don't send window updates if stream is half-closed
                    # Enqueue the write to be processed by the main loop
                    async def do_send() -> None:
                        msg = ServerToClient(
                            stream_id=stream_id,
                            window_update=window,
                        )
                        await self.enqueue_write(msg)

                    asyncio.create_task(do_send())

                def measure_frame(frame: Any) -> int:
                    """Measure the size of a frame for flow control."""
                    if frame.HasField("request_message"):
                        return len(frame.request_message.data)
                    elif frame.HasField("more_request_data"):
                        return len(frame.more_request_data)
                    return 0

                sender = new_sender(send_func, new_stream_msg.initial_window_size)
                receiver = new_receiver(
                    measure_frame, send_window_update, INITIAL_WINDOW_SIZE
                )

            # Create the stream
            server_stream = TunnelServerStream(
                server=self,
                tunnel_stream=tunnel_stream,
                stream_id=stream_id,
                method_name=method_name,
                sender=sender,
                receiver=receiver,
                handler=handler_info.handler,
                is_client_stream=handler_info.is_client_stream,
                is_server_stream=handler_info.is_server_stream,
                headers=headers,
            )

            self._streams[stream_id] = server_stream

            # Start serving the stream in background
            asyncio.create_task(server_stream._serve_stream())

        return True, None

    async def _get_stream(self, stream_id: int) -> Optional["TunnelServerStream"]:
        """Get a stream by ID, or None if it doesn't exist."""
        async with self._stream_lock:
            # Check if stream is active
            target = self._streams.get(stream_id)
            if target is not None:
                return target

            # If stream ID was already seen, ignore (late message)
            if stream_id <= self._last_seen:
                return None

            # Stream never created - protocol error
            raise Exception(f"received frame for stream ID {stream_id}: stream never created")

    async def _remove_stream(self, stream_id: int) -> None:
        """Remove a stream from the active streams map."""
        async with self._stream_lock:
            self._streams.pop(stream_id, None)


class TunnelServerStream:
    """
    Server-side implementation of a single tunneled stream.

    This class implements the server side of a single RPC call within the tunnel,
    handling message send/receive with flow control, headers/trailers, and
    dispatching to the actual service handler.
    """

    def __init__(
        self,
        server: TunnelServer,
        tunnel_stream: grpc.aio.StreamStreamCall[ClientToServer, ServerToClient],
        stream_id: int,
        method_name: str,
        sender: Sender,
        receiver: Receiver[Any],
        handler: Callable[..., Any],
        is_client_stream: bool,
        is_server_stream: bool,
        headers: grpc.aio.Metadata,
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

        # Cancellation tracking
        self._tunnel_stream_closed = False
        self._cancellation_event = asyncio.Event()

        # Locks
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()

        # Context for handler
        self._context = _ServerContext(self)

        # Start stream monitor if done() method available
        # (gRPC AsyncIO streams have done() method in newer versions)
        if hasattr(self._tunnel_stream, 'done') and callable(getattr(self._tunnel_stream, 'done')):
            self._monitor_task: Optional[asyncio.Task[None]] = asyncio.create_task(self._monitor_tunnel_stream())
        else:
            self._monitor_task = None
            logger.debug(
                f"Stream monitoring not available for stream {stream_id} "
                "(gRPC stream doesn't support done() method)"
            )

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

    async def _safe_tunnel_write(
        self,
        msg: ServerToClient,
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

    async def _accept_client_frame(self, msg: ClientToServer) -> None:
        """Accept and process a frame from the client."""
        # Handle half-close
        if msg.HasField("half_close"):
            await self._half_close(None)
            return

        # Handle cancel
        if msg.HasField("cancel"):
            err = Exception("cancelled")
            await self._finish_stream(err)
            return

        # Handle window update
        if msg.HasField("window_update"):
            self._sender.update_window(msg.window_update)
            return

        # Handle message data
        if msg.HasField("request_message") or msg.HasField("more_request_data"):
            try:
                await self._receiver.accept(msg)
            except Exception as e:
                await self._finish_stream(e)
            return

    async def _serve_stream(self) -> None:
        """Serve this stream by invoking the handler."""
        err: Optional[Exception] = None

        try:
            # For unary methods, receive request, invoke handler, send response
            if not self._is_client_stream and not self._is_server_stream:
                # Unary-unary
                request = await self.recv_message()
                response = await self._handler(request, self._context)
                await self.send_message(response)
            elif self._is_client_stream and not self._is_server_stream:
                # Stream-unary
                response = await self._handler(self, self._context)
                await self.send_message(response)
            elif not self._is_client_stream and self._is_server_stream:
                # Unary-stream
                request = await self.recv_message()
                await self._handler(request, self, self._context)
            else:
                # Stream-stream
                await self._handler(self, self._context)

        except Exception as e:
            import traceback
            traceback.print_exc()
            err = e

        finally:
            await self._finish_stream(err)

    async def send_message(
        self,
        message: Any,
        serializer: Optional[Callable[[Any], bytes]] = None,
    ) -> None:
        """
        Send a message to the client.

        Args:
            message: The message to send (protobuf or other serializable object)
            serializer: Optional serializer function. If not provided, assumes
                        message is a protobuf Message.
        """
        async with self._write_lock:
            # Send headers if not already sent
            if not self._sent_headers:
                await self._send_headers_locked()

            # Check if we're allowed to send another message
            if not self._is_server_stream and self._num_sent >= 1:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.INTERNAL,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"Already sent response for non-server-stream method {self._method_name}",
                )

            self._num_sent += 1

            # Serialize message
            if serializer:
                data = serializer(message)
            elif isinstance(message, ProtoMessage):
                data = message.SerializeToString()
            else:
                data = message

            # Send with flow control
            await self._sender.send(data)

    async def recv_message(
        self,
        deserializer: Optional[Callable[[bytes], Any]] = None,
    ) -> Any:
        """
        Receive a message from the client.

        Args:
            deserializer: Optional deserializer function. If not provided,
                          returns raw bytes.

        Returns:
            The deserialized message
        """
        async with self._read_lock:
            data = await self._recv_message_locked()

            # Check if we should fail if there's another message (for unary methods)
            if not self._is_client_stream:
                # Try to read another message - should get EOF
                try:
                    await self._recv_message_locked()
                    # If we got here, there's an extra message
                    err = grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INVALID_ARGUMENT,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details=f"Already received request for non-client-stream method {self._method_name}",
                    )
                    self._read_err = err
                    raise err
                except StopAsyncIteration:
                    # Expected EOF
                    pass

            # Deserialize
            if deserializer:
                result: Any = deserializer(data)
                return result
            return data

    async def _recv_message_locked(self) -> bytes:
        """Receive a single message (must hold read lock)."""
        if self._read_err is not None:
            raise self._read_err

        msg_size = -1
        data = b""

        while True:
            # Dequeue next frame
            frame, ok = await self._receiver.dequeue()

            if not ok or frame is None:
                # Stream closed
                if self._half_closed_err is not None:
                    self._read_err = self._half_closed_err
                    raise self._half_closed_err
                raise StopAsyncIteration()

            # Handle message frames
            if frame.HasField("request_message"):
                if msg_size != -1:
                    err = grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INVALID_ARGUMENT,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details="received request message envelope before previous message finished",
                    )
                    self._read_err = err
                    raise err

                msg_size = frame.request_message.size
                data = bytes(frame.request_message.data)

                if len(data) >= msg_size:
                    return data

            elif frame.HasField("more_request_data"):
                if msg_size == -1:
                    err = grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INVALID_ARGUMENT,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details="never received envelope for request message",
                    )
                    self._read_err = err
                    raise err

                data += bytes(frame.more_request_data)

                if len(data) >= msg_size:
                    return data

    async def set_response_headers(self, headers: grpc.aio.Metadata) -> None:
        """Set response headers (must be called before sending any messages)."""
        async with self._write_lock:
            if self._sent_headers:
                raise Exception("already sent headers")
            if self._response_headers is None:
                self._response_headers = headers
            else:
                # Merge with existing headers
                self._response_headers = grpc.aio.Metadata(
                    *self._response_headers, *headers
                )

    async def send_response_headers(self, headers: grpc.aio.Metadata) -> None:
        """Send response headers immediately."""
        async with self._write_lock:
            if self._sent_headers:
                raise Exception("already sent headers")
            if self._response_headers is None:
                self._response_headers = headers
            else:
                self._response_headers = grpc.aio.Metadata(
                    *self._response_headers, *headers
                )
            await self._send_headers_locked()

    async def _send_headers_locked(self) -> None:
        """Send response headers (must hold write lock)."""
        if self._sent_headers:
            return

        headers_proto = to_proto(self._response_headers)
        msg = ServerToClient(
            stream_id=self._stream_id,
            response_headers=headers_proto,
        )
        await self._server.enqueue_write(msg)
        self._sent_headers = True
        self._response_headers = None

    async def set_response_trailers(self, trailers: grpc.aio.Metadata) -> None:
        """Set response trailers (sent when stream closes)."""
        async with self._write_lock:
            if self._closed:
                raise Exception("already finished")
            if self._response_trailers is None:
                self._response_trailers = trailers
            else:
                self._response_trailers = grpc.aio.Metadata(
                    *self._response_trailers, *trailers
                )

    async def _half_close(self, err: Optional[Exception]) -> None:
        """Mark the stream as half-closed (no more data from client)."""
        if self._half_closed_err is not None:
            # Already half-closed
            return

        if err is None:
            err = StopAsyncIteration()

        self._half_closed_err = err
        self._receiver.close()

    async def _finish_stream(self, err: Optional[Exception]) -> None:
        """Finish the stream and send close message to client."""
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

            # Send close message via server's write queue to avoid concurrent ops
            if send_headers and headers is not None:
                headers_msg = ServerToClient(
                    stream_id=self._stream_id,
                    response_headers=to_proto(headers),
                )
                await self._server.enqueue_write(headers_msg)

            close_msg = ServerToClient(
                stream_id=self._stream_id,
                close_stream={
                    "status": status,
                    "response_trailers": to_proto(trailers),
                },
            )
            await self._server.enqueue_write(close_msg)

            # Clear state
            self._sent_headers = True
            self._response_headers = None
            self._response_trailers = None


class _ServerContext:
    """Context object passed to server handlers."""

    def __init__(self, stream: TunnelServerStream):
        self._stream = stream

    def invocation_metadata(self) -> grpc.aio.Metadata:
        """Get the request headers metadata."""
        return self._stream._request_headers

    async def set_trailing_metadata(self, metadata: grpc.aio.Metadata) -> None:
        """Set trailing metadata (trailers)."""
        await self._stream.set_response_trailers(metadata)

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

    async def wait_for_cancellation(self) -> None:
        """
        Wait until the client disconnects.

        This can be used with asyncio.wait() to race handler execution
        against client disconnection.

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


def _error_to_status(err: Optional[Exception]) -> status_pb2.Status:
    """Convert an exception to a gRPC status."""
    if err is None:
        return status_pb2.Status(code=0)  # OK

    # Check for AioRpcError which has code() and details() methods
    if isinstance(err, grpc.aio.AioRpcError):
        return status_pb2.Status(
            code=err.code().value[0],
            message=err.details() or "",
        )

    if isinstance(err, asyncio.CancelledError):
        return status_pb2.Status(
            code=grpc.StatusCode.CANCELLED.value[0],
            message="cancelled",
        )

    # Unknown error
    return status_pb2.Status(
        code=grpc.StatusCode.UNKNOWN.value[0],
        message=str(err),
    )
