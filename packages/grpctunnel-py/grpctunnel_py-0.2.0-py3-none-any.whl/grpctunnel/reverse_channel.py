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

"""Reverse tunnel channel implementation.

This module provides the ReverseTunnelChannel, which wraps a reverse tunnel
stream and allows the server to send RPCs back to the client.
"""

import asyncio
from typing import Any, Callable, Optional

import grpc

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
)


class ReverseTunnelChannel:
    """A channel for sending RPCs from server to client over a reverse tunnel.

    This channel wraps a reverse tunnel stream where the message directions are
    inverted compared to forward tunnels.
    """

    def __init__(
        self,
        stream_adapter: Any,
        options: Optional[TunnelOptions] = None,
        client_will_send_settings: bool = True,
    ):
        """Initialize a reverse tunnel channel.

        Args:
            stream_adapter: The reverse tunnel stream adapter
            options: Optional tunnel configuration
            client_will_send_settings: Whether to expect settings from client
        """
        self._adapter = stream_adapter
        self._options = options or TunnelOptions()
        self._client_will_send_settings = client_will_send_settings

        # Stream management
        self._streams: dict[int, "ReverseTunnelClientStream"] = {}
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

        # Send queue
        self._send_queue: asyncio.Queue[Optional[ClientToServer]] = asyncio.Queue()

        # Start loops
        self._send_task = asyncio.create_task(self._send_loop())
        self._recv_task = asyncio.create_task(self._recv_loop())

    async def _send_loop(self) -> None:
        """Background task to send messages."""
        try:
            # In reverse tunnels, the server (acting as client) doesn't send settings
            # Instead, it receives settings from the client (acting as server)
            # If client won't send settings, we can start immediately
            if not self._client_will_send_settings:
                self._use_revision = REVISION_ZERO
                self._settings_event.set()

            while not self._closed:
                try:
                    msg = await asyncio.wait_for(self._send_queue.get(), timeout=0.1)
                    if msg is None:
                        break
                    await self._adapter.write(msg)
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            await self._close(e)

    async def _recv_loop(self) -> None:
        """Background task to receive messages."""
        try:
            while not self._closed:
                msg = await self._adapter.read()
                if msg is None:
                    break

                # Handle settings message (from client acting as server)
                if msg.stream_id == -1 and msg.HasField("settings"):
                    self._settings = msg.settings
                    # Determine protocol revision from settings
                    if msg.settings.supported_protocol_revisions:
                        # Use highest supported revision
                        self._use_revision = max(msg.settings.supported_protocol_revisions)
                    else:
                        self._use_revision = REVISION_ZERO
                    self._settings_event.set()
                    continue

                stream = await self._get_stream(msg.stream_id)
                if stream is not None:
                    await stream._accept_client_frame(msg)
        except Exception as e:
            await self._close(e)

    async def _get_stream(self, stream_id: int) -> Optional["ReverseTunnelClientStream"]:
        """Get a stream by ID."""
        async with self._stream_lock:
            return self._streams.get(stream_id)

    async def _remove_stream(self, stream_id: int) -> None:
        """Remove a stream from active streams."""
        async with self._stream_lock:
            self._streams.pop(stream_id, None)

    async def _close(self, error: Optional[Exception] = None) -> None:
        """Close the channel."""
        async with self._stream_lock:
            if self._closed:
                return
            self._closed = True
            self._error = error

            for stream in list(self._streams.values()):
                stream._cancel()

            self._streams.clear()
            self._done_event.set()
            await self._send_queue.put(None)

            if not self._send_task.done():
                self._send_task.cancel()
            if not self._recv_task.done():
                self._recv_task.cancel()

    async def close_async(self) -> None:
        """Close the channel asynchronously."""
        await self._close(None)

    def close(self) -> None:
        """Close the channel synchronously."""
        if not self._closed:
            asyncio.create_task(self._close(None))

    async def _allocate_stream(
        self, method: str, metadata: Optional[grpc.aio.Metadata] = None
    ) -> "ReverseTunnelClientStream":
        """Allocate a new stream for an RPC."""
        await self._settings_event.wait()

        async with self._stream_lock:
            if self._closed:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.CANCELLED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="Channel is closed",
                )

            self._last_stream_id += 1
            stream_id = self._last_stream_id

            # Create sender and receiver
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
                    lambda window_update: self._send_window_update(stream_id, window_update),
                    INITIAL_WINDOW_SIZE,
                )

            stream = ReverseTunnelClientStream(
                channel=self,
                stream_id=stream_id,
                method=method,
                sender=sender,
                receiver=receiver,
            )

            self._streams[stream_id] = stream
            return stream

    async def _send_new_stream(
        self, stream: "ReverseTunnelClientStream", metadata: Optional[grpc.aio.Metadata] = None
    ) -> None:
        """Send NewStream message."""
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
        """Send request data."""
        if first:
            msg = ClientToServer(
                stream_id=stream_id,
                request_message={"size": total_size, "data": data},
            )
        else:
            msg = ClientToServer(stream_id=stream_id, more_request_data=data)
        await self._send_queue.put(msg)

    def _send_window_update(self, stream_id: int, window_update: int) -> None:
        """Send window update."""
        self._send_queue.put_nowait(
            ClientToServer(stream_id=stream_id, window_update=window_update)
        )

    def _measure_frame(self, frame: Any) -> int:
        """Measure frame size for flow control."""
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
    ) -> Any:
        """Create a unary-unary RPC method."""

        async def _unary_unary_call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            await stream.send_message(request, request_serializer)
            await stream.close_send()

            response = await stream.receive_message(response_deserializer)
            return response

        return _unary_unary_call

    def unary_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> Any:
        """Create a unary-stream RPC method."""

        async def _unary_stream_call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            await stream.send_message(request, request_serializer)
            await stream.close_send()

            class ResponseIterator:
                def __init__(self, stream):
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
    ) -> Any:
        """Create a stream-unary RPC method."""

        async def _stream_unary_call(
            request_iterator: Optional[Any] = None,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            if request_iterator is not None:
                async for request in request_iterator:
                    await stream.send_message(request, request_serializer)

            await stream.close_send()
            response = await stream.receive_message(response_deserializer)
            return response

        return _stream_unary_call

    def stream_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> Any:
        """Create a stream-stream (bidirectional) RPC method."""

        async def _stream_stream_call(
            request_iterator: Optional[Any] = None,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            async with self._stream_creation_lock:
                stream = await self._allocate_stream(method, metadata)
                await self._send_new_stream(stream, metadata)

            class BidiStream:
                def __init__(self, stream):
                    self._stream = stream
                    self._request_serializer = request_serializer
                    self._response_deserializer = response_deserializer

                async def write(self, request):
                    await self._stream.send_message(request, self._request_serializer)

                async def done_writing(self):
                    await self._stream.close_send()

                async def read(self):
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
            if request_iterator is not None:

                async def send_requests():
                    try:
                        async for request in request_iterator:
                            await bidi.write(request)
                        await bidi.done_writing()
                    except Exception:
                        pass

                asyncio.create_task(send_requests())

            return bidi

        return _stream_stream_call


class ReverseTunnelClientStream:
    """A single RPC stream within a reverse tunnel."""

    def __init__(
        self,
        channel: ReverseTunnelChannel,
        stream_id: int,
        method: str,
        sender: Sender,
        receiver: Receiver[Any],
    ):
        """Initialize the stream."""
        self._channel = channel
        self._stream_id = stream_id
        self._method = method
        self._sender = sender
        self._receiver = receiver

        self._cancelled = False
        self._done = False
        self._error: Optional[Exception] = None
        self._done_event = asyncio.Event()

        self._headers: Optional[grpc.aio.Metadata] = None
        self._headers_event = asyncio.Event()
        self._trailers: Optional[grpc.aio.Metadata] = None

        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._half_closed = False

    async def _accept_client_frame(self, msg: ServerToClient) -> None:
        """Accept a frame from the client."""
        if msg.HasField("response_headers"):
            await self._handle_headers(msg.response_headers)
        elif msg.HasField("response_message") or msg.HasField("more_response_data"):
            await self._receiver.accept(msg)
        elif msg.HasField("close_stream"):
            await self._handle_close(msg.close_stream)
        elif msg.HasField("window_update"):
            self._sender.update_window(msg.window_update)

    async def _handle_headers(self, headers_proto: Any) -> None:
        """Handle response headers."""
        if self._headers is not None:
            return
        self._headers = from_proto(headers_proto)
        self._headers_event.set()

    async def _handle_close(self, close_msg: Any) -> None:
        """Handle stream close."""
        self._trailers = from_proto(close_msg.response_trailers)
        if close_msg.status and close_msg.status.code != 0:
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
        self, message: Any, serializer: Optional[Callable[[Any], bytes]] = None
    ) -> None:
        """Send a message."""
        async with self._write_lock:
            from google.protobuf.message import Message as ProtoMessage

            if serializer:
                data = serializer(message)
            elif isinstance(message, ProtoMessage):
                data = message.SerializeToString()
            else:
                raise ValueError(f"Cannot serialize message of type {type(message)}")

            await self._sender.send(data)

    async def receive_message(
        self, deserializer: Optional[Callable[[bytes], Any]] = None
    ) -> Any:
        """Receive a message."""
        async with self._read_lock:
            msg_size = -1
            data = b""

            while True:
                frame, ok = await self._receiver.dequeue()
                if not ok or frame is None:
                    if self._error:
                        raise self._error
                    raise grpc.aio.AioRpcError(
                        code=grpc.StatusCode.CANCELLED,
                        initial_metadata=grpc.aio.Metadata(),
                        trailing_metadata=self._trailers or grpc.aio.Metadata(),
                        details="Stream closed",
                    )

                if frame.HasField("response_message"):
                    if msg_size != -1:
                        raise grpc.aio.AioRpcError(
                            code=grpc.StatusCode.INTERNAL,
                            initial_metadata=grpc.aio.Metadata(),
                            trailing_metadata=grpc.aio.Metadata(),
                            details="Client sent response message envelope before previous message finished",
                        )
                    msg_size = frame.response_message.size
                    data = frame.response_message.data
                    if len(data) >= msg_size:
                        break
                elif frame.HasField("more_response_data"):
                    if msg_size == -1:
                        raise grpc.aio.AioRpcError(
                            code=grpc.StatusCode.INTERNAL,
                            initial_metadata=grpc.aio.Metadata(),
                            trailing_metadata=grpc.aio.Metadata(),
                            details="Client never sent envelope for response message",
                        )
                    data += frame.more_response_data
                    if len(data) >= msg_size:
                        break

            if deserializer:
                return deserializer(data)
            else:
                return data

    async def close_send(self) -> None:
        """Close the send side."""
        async with self._write_lock:
            if self._half_closed:
                return
            self._half_closed = True
            from google.protobuf import empty_pb2

            await self._channel._send_queue.put(
                ClientToServer(
                    stream_id=self._stream_id,
                    half_close=empty_pb2.Empty(),
                )
            )

    def _cancel(self) -> None:
        """Cancel the stream."""
        if not self._cancelled and not self._done:
            self._cancelled = True
            self._receiver.cancel()
