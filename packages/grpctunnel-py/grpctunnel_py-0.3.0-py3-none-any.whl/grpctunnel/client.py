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

"""Forward tunnel client implementation.

This module provides the TunnelChannel, which implements grpc.aio.Channel
and allows RPCs to be tunneled over an existing gRPC stream.
"""

import asyncio
from typing import Any, Callable, Optional

import grpc
from google.protobuf import empty_pb2
from google.protobuf.message import Message as ProtoMessage

# Sentinel for EOF
_EOF = object()

from grpctunnel.flow_control import (
    INITIAL_WINDOW_SIZE,
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
    NewStream,
    ServerToClient,
    TunnelServiceStub,
)

# Protocol negotiation header
GRPCTUNNEL_NEGOTIATE_KEY = "grpctunnel-negotiate"
GRPCTUNNEL_NEGOTIATE_VAL = "on"


class PendingChannel:
    """An un-started channel that can be started to create a tunnel.

    Calling start() will establish the tunnel and return a TunnelChannel
    that implements grpc.aio.Channel, so it can be used to create stubs
    and issue RPCs that are all carried over a single tunnel stream.
    """

    def __init__(self, stub: TunnelServiceStub, options: Optional[TunnelOptions] = None):
        """Initialize a pending channel.

        Args:
            stub: The TunnelService stub to use for opening the tunnel
            options: Tunnel configuration options
        """
        self._stub = stub
        self._options = options or TunnelOptions()

    async def start(self, **kwargs: Any) -> "TunnelChannel":
        """Start the tunnel and return a usable channel.

        Args:
            **kwargs: Additional options to pass to OpenTunnel (e.g., metadata, timeout)

        Returns:
            A TunnelChannel that can be used for RPCs

        Raises:
            grpc.RpcError: If the tunnel cannot be established
        """
        # Add negotiation header to indicate we support protocol revision negotiation
        metadata = kwargs.get("metadata", grpc.aio.Metadata())
        metadata = grpc.aio.Metadata(
            *metadata, (GRPCTUNNEL_NEGOTIATE_KEY, GRPCTUNNEL_NEGOTIATE_VAL)
        )
        kwargs["metadata"] = metadata

        # Open the tunnel stream
        stream = self._stub.OpenTunnel(**kwargs)

        # Get response headers to check if server supports settings negotiation
        try:
            resp_metadata = await stream.initial_metadata()
        except Exception as e:
            raise grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNAVAILABLE,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details=f"Failed to get initial metadata from tunnel: {e}",
            )

        # Check if server sends settings
        server_sends_settings = False
        if resp_metadata:
            for key, value in resp_metadata:
                if key == GRPCTUNNEL_NEGOTIATE_KEY and value == GRPCTUNNEL_NEGOTIATE_VAL:
                    server_sends_settings = True
                    break

        # Get request metadata for tunnel context
        tunnel_metadata = metadata

        # Create and return the tunnel channel
        return TunnelChannel(
            stream=stream,
            tunnel_metadata=tunnel_metadata,
            server_sends_settings=server_sends_settings,
            options=self._options,
        )


class TunnelChannel(grpc.aio.Channel):
    """A gRPC channel that tunnels RPCs over an existing gRPC stream.

    This channel implements grpc.aio.Channel and can be used to create
    stubs and issue RPCs. All RPCs are multiplexed over a single tunnel stream.

    Thread Safety:
        - All writes to the underlying stream go through _send_queue, ensuring serialization
        - Stream management operations are protected by _stream_lock
        - Stream creation is protected by _stream_creation_lock
        - Only one _send_loop and one _recv_loop run per channel
        - Individual streams have their own read/write locks
    """

    def __init__(
        self,
        stream: Any,  # grpc.aio.StreamStreamCall
        tunnel_metadata: grpc.aio.Metadata,
        server_sends_settings: bool,
        options: TunnelOptions,
    ):
        """Initialize the tunnel channel.

        Args:
            stream: The underlying tunnel stream
            tunnel_metadata: Metadata used to open the tunnel
            server_sends_settings: Whether server sends settings message
            options: Tunnel configuration options
        """
        self._stream = stream
        self._tunnel_metadata = tunnel_metadata
        self._server_sends_settings = server_sends_settings
        self._options = options

        # Stream management
        self._streams: dict[int, "TunnelClientStream"] = {}
        self._last_stream_id = 0
        self._stream_lock = asyncio.Lock()
        self._stream_creation_lock = asyncio.Lock()

        # Channel state
        self._closed = False
        self._error: Optional[Exception] = None
        self._done_event = asyncio.Event()

        # Settings negotiation
        self._settings_event = asyncio.Event()
        self._settings: Optional[Any] = None
        self._use_revision = REVISION_ZERO

        # Send queue to keep write side of tunnel open
        self._send_queue: asyncio.Queue[Optional[ClientToServer]] = asyncio.Queue()

        # Store the stream context for context() method
        # In Python, we don't have Go-style contexts, but we can store stream metadata
        self._context = {"stream": stream, "tunnel_metadata": tunnel_metadata}

        # Start send and receive loops
        self._send_task = asyncio.create_task(self._send_loop())
        self._recv_task = asyncio.create_task(self._recv_loop())

    async def _send_loop(self) -> None:
        """Background task to send messages to the tunnel stream.

        This method is thread-safe: all sends go through the queue,
        ensuring serialized access to the stream's write method.
        """
        try:
            while not self._closed:
                # Get message from queue with timeout to keep stream alive
                try:
                    msg = await asyncio.wait_for(self._send_queue.get(), timeout=0.1)
                    if msg is None:  # Sentinel to close
                        break
                    # Write to stream (only one writer at a time via queue)
                    await self._stream.write(msg)
                except asyncio.TimeoutError:
                    # No message available, but we need to keep the write side active
                    # Just continue the loop - the act of looping keeps us active
                    continue
        except Exception as e:
            await self._close(e)

    async def _recv_loop(self) -> None:
        """Background task to receive messages from the tunnel stream.

        This method is thread-safe: only one recv_loop runs per channel,
        ensuring serialized access to the stream's read method.
        """
        try:
            # Wait for settings if server sends them
            if self._server_sends_settings:
                msg = await self._stream.read()
                if msg is None:
                    raise grpc.aio.AioRpcError(
                        code=grpc.StatusCode.UNAVAILABLE,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details="Stream closed before receiving settings",
                    )

                # Validate settings message
                if msg.stream_id != -1:
                    raise grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INTERNAL,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details=f"Protocol error: settings frame had bad stream ID ({msg.stream_id})",
                    )

                if not msg.HasField("settings"):
                    raise grpc.aio.AioRpcError(
                        code=grpc.StatusCode.INTERNAL,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details="Protocol error: first frame was not settings",
                    )

                # Negotiate protocol revision
                settings = msg.settings
                supported_revisions = self._options.supported_revisions()
                supported = False
                for rev in settings.supported_protocol_revisions:
                    if rev in supported_revisions:
                        if rev > self._use_revision:
                            self._use_revision = rev
                        supported = True

                if not supported:
                    raise grpc.aio.AioRpcError(
                        code=grpc.StatusCode.UNIMPLEMENTED,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=grpc.aio.Metadata(),
                        details=f"Protocol error: server supports revisions {settings.supported_protocol_revisions}, "
                        f"but client supports {supported_revisions}",
                    )

                self._settings = settings

            # Signal that settings are ready
            self._settings_event.set()

            # Main receive loop - continue using read() API consistently
            while not self._closed:
                msg = await self._stream.read()
                if msg is None:
                    break
                stream = await self._get_stream(msg.stream_id)
                if stream is not None:
                    await stream._accept_server_frame(msg)

        except Exception as e:
            await self._close(e)

    async def _get_stream(self, stream_id: int) -> Optional["TunnelClientStream"]:
        """Get a stream by ID."""
        async with self._stream_lock:
            return self._streams.get(stream_id)

    async def _remove_stream(self, stream_id: int) -> None:
        """Remove a stream from the active streams map."""
        async with self._stream_lock:
            self._streams.pop(stream_id, None)

    async def _close(self, error: Optional[Exception] = None) -> None:
        """Close the channel and all active streams."""
        async with self._stream_lock:
            if self._closed:
                return

            self._closed = True
            self._error = error if error is not None else _EOF  # type: ignore

            # Cancel all active streams
            for stream in list(self._streams.values()):
                stream._cancel()

            self._streams.clear()
            self._done_event.set()

            # Stop send loop
            await self._send_queue.put(None)

            # Cancel tasks if still running
            if not self._send_task.done():
                self._send_task.cancel()
            if not self._recv_task.done():
                self._recv_task.cancel()

    def close(self) -> None:
        """Close the channel synchronously."""
        if not self._closed:
            asyncio.create_task(self._close(None))

    async def close_async(self) -> None:
        """Close the channel asynchronously."""
        await self._close(None)

    def done(self) -> asyncio.Event:
        """Return an event that can be awaited for channel closing.

        This method provides Go-like channel semantics for Python.
        In Go, Done() returns a channel. In Python, we return an asyncio.Event
        that can be awaited using `await channel.done().wait()`.

        Returns:
            An asyncio.Event that is set when the channel is closed.
        """
        return self._done_event

    def err(self) -> Optional[Exception]:
        """Return the error that caused the channel to close.

        Returns:
            The exception that caused the channel to close, or None if the
            channel is still open or closed normally.
        """
        if not self._closed:
            return None
        # Don't return _EOF sentinel, return None for normal closure
        if self._error is _EOF:
            return None
        return self._error

    def context(self) -> dict:
        """Return the context associated with this channel.

        For forward tunnels, this includes the outgoing metadata (request headers)
        that were used to open the tunnel. For reverse tunnels, this would include
        incoming metadata.

        Returns:
            A dictionary containing context information including the stream
            and tunnel metadata.
        """
        return self._context

    async def wait_for_termination(self, timeout: Optional[float] = None) -> bool:
        """Wait for the channel to terminate.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            True if channel terminated, False if timeout occurred
        """
        try:
            await asyncio.wait_for(self._done_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def get_state(self, try_to_connect: bool = False) -> grpc.ChannelConnectivity:
        """Get the current connectivity state of the channel."""
        if self._closed:
            return grpc.ChannelConnectivity.SHUTDOWN
        if self._settings_event.is_set():
            return grpc.ChannelConnectivity.READY
        return grpc.ChannelConnectivity.CONNECTING

    async def channel_ready(self) -> None:
        """Wait for the channel to be ready."""
        await self._settings_event.wait()

    async def _allocate_stream(
        self,
        method: str,
        metadata: Optional[grpc.aio.Metadata] = None,
    ) -> "TunnelClientStream":
        """Allocate a new stream for an RPC.

        Args:
            method: The RPC method name
            metadata: Optional metadata for the RPC

        Returns:
            A new TunnelClientStream

        Raises:
            grpc.RpcError: If stream allocation fails
        """
        # Wait for settings to be ready
        await self._settings_event.wait()

        async with self._stream_lock:
            if self._closed:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.CANCELLED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="Channel is closed",
                )

            # Allocate new stream ID
            self._last_stream_id += 1
            stream_id = self._last_stream_id

            # Create sender and receiver based on protocol revision
            if self._use_revision == REVISION_ZERO:
                sender = new_sender_without_flow_control(
                    lambda data, total_size, first: self._send_request_data(
                        stream_id, data, total_size, first
                    )
                )
                receiver: Receiver[Any] = new_receiver_without_flow_control()
            else:
                sender = new_sender(
                    lambda data, total_size, first: self._send_request_data(
                        stream_id, data, total_size, first
                    ),
                    INITIAL_WINDOW_SIZE,
                )
                receiver = new_receiver(
                    lambda frame: self._measure_frame(frame),
                    lambda window_update: self._send_window_update(
                        stream_id, window_update
                    ),
                    self._settings.initial_window_size
                    if self._settings
                    else INITIAL_WINDOW_SIZE,
                )

            # Create stream
            stream = TunnelClientStream(
                channel=self,
                stream_id=stream_id,
                method=method,
                sender=sender,
                receiver=receiver,
            )

            # Register stream
            self._streams[stream_id] = stream

            return stream

    async def _send_new_stream(
        self, stream: "TunnelClientStream", metadata: Optional[grpc.aio.Metadata] = None
    ) -> None:
        """Send the NewStream message to start an RPC.

        Args:
            stream: The stream to start
            metadata: Optional metadata for the RPC
        """
        # Send NewStream message
        msg = ClientToServer(
            stream_id=stream._stream_id,
            new_stream=NewStream(
                method_name=stream._method,
                request_headers=to_proto(metadata),
                protocol_revision=self._use_revision,
                initial_window_size=INITIAL_WINDOW_SIZE,
            ),
        )
        await self._send_queue.put(msg)

    async def _send_request_data(
        self, stream_id: int, data: bytes, total_size: int, first: bool
    ) -> None:
        """Send request data for a stream.

        Args:
            stream_id: The stream ID
            data: The data chunk to send
            total_size: Total message size
            first: Whether this is the first chunk
        """
        if first:
            msg = ClientToServer(
                stream_id=stream_id,
                request_message={"size": total_size, "data": data},
            )
        else:
            msg = ClientToServer(stream_id=stream_id, more_request_data=data)
        await self._send_queue.put(msg)

    def _send_window_update(self, stream_id: int, window_update: int) -> None:
        """Send a window update for flow control.

        Args:
            stream_id: The stream ID
            window_update: The window update amount
        """
        # Queue the message (non-async, so we use put_nowait)
        self._send_queue.put_nowait(
            ClientToServer(stream_id=stream_id, window_update=window_update)
        )

    def _measure_frame(self, frame: Any) -> int:
        """Measure the size of a frame for flow control.

        Args:
            frame: The frame to measure

        Returns:
            The size in bytes
        """
        # This is a simplified measurement
        if frame.HasField("response_message"):
            return len(frame.response_message.data)
        elif frame.HasField("more_response_data"):
            return len(frame.more_response_data)
        return 0

    def unary_unary(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> grpc.aio.UnaryUnaryMultiCallable:
        """Create a unary-unary RPC method."""
        # Return a callable that performs the unary-unary RPC
        async def _unary_unary_call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            # Allocate stream
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            # Send request
            await stream.send_message(request, request_serializer)
            await stream.close_send()

            # Receive response
            response = await stream.receive_message(response_deserializer)
            return response

        return _unary_unary_call

    def unary_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> grpc.aio.UnaryStreamMultiCallable:
        """Create a unary-stream RPC method."""
        async def _unary_stream_call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            # Allocate stream
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            # Send request and half-close
            await stream.send_message(request, request_serializer)
            await stream.close_send()

            # Return an async iterator for responses
            class ResponseIterator:
                def __init__(self, stream: "TunnelClientStream"):
                    self._stream = stream

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    try:
                        return await self._stream.receive_message(response_deserializer)
                    except grpc.RpcError as e:
                        if e.code() == grpc.StatusCode.CANCELLED:
                            raise StopAsyncIteration
                        raise

            return ResponseIterator(stream)

        return _unary_stream_call

    def stream_unary(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> grpc.aio.StreamUnaryMultiCallable:
        """Create a stream-unary RPC method."""
        async def _stream_unary_call(
            request_iterator: Any = None,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            # Allocate stream
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            # If request_iterator is provided, send all requests
            if request_iterator is not None:
                async for request in request_iterator:
                    await stream.send_message(request, request_serializer)

            # Half-close
            await stream.close_send()

            # Receive single response
            response = await stream.receive_message(response_deserializer)
            return response

        return _stream_unary_call

    def stream_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> grpc.aio.StreamStreamMultiCallable:
        """Create a stream-stream (bidirectional) RPC method."""
        async def _stream_stream_call(
            request_iterator: Any = None,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            # Allocate stream
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            # Return a bidirectional stream object
            class BidiStream:
                def __init__(self, stream: "TunnelClientStream"):
                    self._stream = stream
                    self._request_serializer = request_serializer
                    self._response_deserializer = response_deserializer

                async def write(self, request: Any) -> None:
                    await self._stream.send_message(request, self._request_serializer)

                async def done_writing(self) -> None:
                    await self._stream.close_send()

                async def read(self) -> Any:
                    try:
                        return await self._stream.receive_message(self._response_deserializer)
                    except grpc.RpcError as e:
                        if e.code() == grpc.StatusCode.CANCELLED:
                            return None
                        raise

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    msg = await self.read()
                    if msg is None:
                        raise StopAsyncIteration
                    return msg

            bidi = BidiStream(stream)

            # If request_iterator is provided, start sending in background
            if request_iterator is not None:
                async def send_requests():
                    try:
                        async for request in request_iterator:
                            await bidi.write(request)
                        await bidi.done_writing()
                    except Exception:
                        pass  # Errors will be surfaced on read side

                asyncio.create_task(send_requests())

            return bidi

        return _stream_stream_call

    async def wait_for_state_change(self, last_observed_state: grpc.ChannelConnectivity) -> None:
        """Wait for the channel state to change from the last observed state.

        Args:
            last_observed_state: The last observed state
        """
        # Simple implementation: wait for termination
        current_state = self.get_state()
        if current_state != last_observed_state:
            return
        await self._done_event.wait()

    async def __aenter__(self) -> "TunnelChannel":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close_async()

    def __del__(self) -> None:
        """Cleanup when the channel is garbage collected."""
        if not self._closed:
            self.close()


class TunnelClientStream:
    """A single RPC stream within a tunnel.

    This class manages the state and communication for one RPC call
    through the tunnel.
    """

    def __init__(
        self,
        channel: TunnelChannel,
        stream_id: int,
        method: str,
        sender: Sender,
        receiver: Receiver[Any],
    ):
        """Initialize a tunnel client stream.

        Args:
            channel: The parent tunnel channel
            stream_id: Unique stream ID
            method: RPC method name
            sender: Sender for flow control
            receiver: Receiver for flow control
        """
        self._channel = channel
        self._stream_id = stream_id
        self._method = method
        self._sender = sender
        self._receiver = receiver

        # Stream state
        self._cancelled = False
        self._done = False
        self._error: Optional[Exception] = None
        self._done_event = asyncio.Event()

        # Metadata
        self._headers: Optional[grpc.aio.Metadata] = None
        self._headers_event = asyncio.Event()
        self._trailers: Optional[grpc.aio.Metadata] = None

        # Message I/O
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._half_closed = False

    async def _accept_server_frame(self, msg: ServerToClient) -> None:
        """Accept a frame from the server for this stream."""
        # Extract the frame from the message
        if msg.HasField("response_headers"):
            await self._handle_headers(msg.response_headers)
        elif msg.HasField("response_message") or msg.HasField("more_response_data"):
            # These are data frames, add entire message to receiver (not just the field)
            # so that receive_message can check HasField("response_message")
            await self._receiver.accept(msg)
        elif msg.HasField("close_stream"):
            await self._handle_close(msg.close_stream)
        elif msg.HasField("window_update"):
            self._sender.update_window(msg.window_update)

    async def _handle_headers(self, headers_proto: Any) -> None:
        """Handle response headers."""
        if self._headers is not None:
            return  # Already got headers
        self._headers = from_proto(headers_proto)
        self._headers_event.set()

    async def _handle_close(self, close_msg: Any) -> None:
        """Handle stream close message."""
        self._trailers = from_proto(close_msg.response_trailers)
        # Convert status to error
        if close_msg.status and close_msg.status.code != 0:
            # Find the StatusCode from the integer value
            status_code = grpc.StatusCode.UNKNOWN
            for sc in grpc.StatusCode:
                if sc.value[0] == close_msg.status.code:
                    status_code = sc
                    break
            self._error = grpc.aio.AioRpcError(
                code=status_code,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=self._trailers or grpc.aio.Metadata(),
                details=close_msg.status.message,
            )
        else:
            self._error = None
        self._done = True
        self._done_event.set()
        self._receiver.close()

    async def send_message(
        self,
        message: Any,
        serializer: Optional[Callable[[Any], bytes]] = None,
    ) -> None:
        """Send a message on this stream.

        Args:
            message: The message to send
            serializer: Optional serializer function
        """
        async with self._write_lock:
            # Serialize message
            if serializer:
                data = serializer(message)
            elif isinstance(message, ProtoMessage):
                data = message.SerializeToString()
            else:
                raise ValueError(f"Cannot serialize message of type {type(message)}")

            # Send via flow control sender
            await self._sender.send(data)

    async def receive_message(
        self, deserializer: Optional[Callable[[bytes], Any]] = None
    ) -> Any:
        """Receive a message from this stream.

        Args:
            deserializer: Optional deserializer function

        Returns:
            The received message

        Raises:
            grpc.RpcError: If the stream is closed or an error occurred
        """
        async with self._read_lock:
            # Collect all chunks for a single message
            msg_size = -1
            data = b""

            while True:
                frame, ok = await self._receiver.dequeue()
                if not ok or frame is None:
                    # Stream closed
                    if self._error:
                        raise self._error
                    raise grpc.aio.AioRpcError(
                        code=grpc.StatusCode.CANCELLED,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=self._trailers or grpc.aio.Metadata(),
                        details="Stream closed",
                    )

                # Handle response_message (first frame with size)
                if frame.HasField("response_message"):
                    if msg_size != -1:
                        raise grpc.aio.AioRpcError(
                            code=grpc.StatusCode.INTERNAL,
                            initial_metadata=grpc.aio.Metadata(),
                            trailing_metadata=grpc.aio.Metadata(),
                            details="Server sent response message envelope before previous message finished",
                        )
                    msg_size = frame.response_message.size
                    data = frame.response_message.data
                    if len(data) >= msg_size:
                        break
                # Handle more_response_data
                elif frame.HasField("more_response_data"):
                    if msg_size == -1:
                        raise grpc.aio.AioRpcError(
                            code=grpc.StatusCode.INTERNAL,
                            initial_metadata=grpc.aio.Metadata(),
                            trailing_metadata=grpc.aio.Metadata(),
                            details="Server never sent envelope for response message",
                        )
                    data += frame.more_response_data
                    if len(data) >= msg_size:
                        break

            # Deserialize
            if deserializer:
                return deserializer(data)
            else:
                # Assume it's a protobuf message - caller must handle
                return data

    async def close_send(self) -> None:
        """Close the send side of the stream (half-close)."""
        async with self._write_lock:
            if self._half_closed:
                return
            self._half_closed = True
            await self._channel._send_queue.put(
                ClientToServer(
                    stream_id=self._stream_id,
                    half_close=empty_pb2.Empty(),
                )
            )

    async def initial_metadata(self) -> Optional[grpc.aio.Metadata]:
        """Get the initial metadata (headers) from the server."""
        await self._headers_event.wait()
        return self._headers

    def trailing_metadata(self) -> Optional[grpc.aio.Metadata]:
        """Get the trailing metadata (trailers) from the server."""
        return self._trailers

    def _cancel(self) -> None:
        """Cancel the stream."""
        if not self._cancelled and not self._done:
            self._cancelled = True
            self._receiver.cancel()
            # Send cancel message to server
            self._channel._send_queue.put_nowait(
                ClientToServer(
                    stream_id=self._stream_id,
                    cancel=empty_pb2.Empty(),
                )
            )


def new_channel(
    stub: TunnelServiceStub, options: Optional[TunnelOptions] = None
) -> PendingChannel:
    """Create a new pending channel.

    Args:
        stub: The TunnelService stub to use for opening the tunnel
        options: Tunnel configuration options

    Returns:
        A PendingChannel that can be started to create a tunnel
    """
    return PendingChannel(stub, options)
