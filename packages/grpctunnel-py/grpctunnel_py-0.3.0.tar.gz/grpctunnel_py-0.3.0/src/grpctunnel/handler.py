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

"""Tunnel service handler implementation.

This module provides the TunnelServiceHandler, which implements the
TunnelService server and manages both forward and reverse tunnels.
"""

import asyncio
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

import grpc
from grpc import aio

from grpctunnel.client import TunnelChannel
from grpctunnel.options import TunnelOptions
from grpctunnel.proto.v1 import (
    TunnelServiceServicer,
    add_TunnelServiceServicer_to_server,
)
from grpctunnel.reverse import _extract_service_metadata
from grpctunnel.reverse_channel import ReverseTunnelChannel
from grpctunnel.server import TunnelServer


@dataclass
class TunnelServiceHandlerOptions:
    """Options for configuring a TunnelServiceHandler.

    Attributes:
        no_reverse_tunnels: If True, reverse tunnels are not allowed
        on_reverse_tunnel_open: Callback when a reverse tunnel is opened
        on_reverse_tunnel_close: Callback when a reverse tunnel closes
        affinity_key: Function to compute affinity key for reverse tunnels
        disable_flow_control: If True, disable flow control
        server_interceptors: Optional sequence of server interceptors for forward tunnels
    """

    no_reverse_tunnels: bool = False
    on_reverse_tunnel_open: Optional[Callable[[TunnelChannel], None]] = None
    on_reverse_tunnel_close: Optional[Callable[[TunnelChannel], None]] = None
    affinity_key: Optional[Callable[[TunnelChannel], Any]] = None
    disable_flow_control: bool = False
    server_interceptors: Optional[Sequence[aio.ServerInterceptor]] = None


class ReverseChannels:
    """Manages a collection of reverse tunnel channels with round-robin selection."""

    def __init__(self):
        self._channels: List[TunnelChannel] = []
        self._index = 0
        self._lock = asyncio.Lock()
        self._ready_event = asyncio.Event()

    async def add(self, channel: TunnelChannel) -> None:
        """Add a channel to the collection."""
        async with self._lock:
            self._channels.append(channel)
            if len(self._channels) == 1:
                self._ready_event.set()

    async def remove(self, channel: TunnelChannel) -> None:
        """Remove a channel from the collection."""
        async with self._lock:
            try:
                self._channels.remove(channel)
                if len(self._channels) == 0:
                    self._ready_event.clear()
            except ValueError:
                pass

    async def pick(self) -> Optional[TunnelChannel]:
        """Pick the next channel using round-robin."""
        async with self._lock:
            if not self._channels:
                return None
            self._index = (self._index + 1) % len(self._channels)
            return self._channels[self._index]

    def ready(self) -> bool:
        """Check if any channels are available."""
        return self._ready_event.is_set()

    async def wait_for_ready(self, timeout: Optional[float] = None) -> bool:
        """Wait for at least one channel to be available.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            True if ready, False if timeout occurred
        """
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def all_channels(self) -> List[TunnelChannel]:
        """Get a snapshot of all channels."""
        async with self._lock:
            return self._channels.copy()


class TunnelServiceHandler:
    """Handler for the TunnelService that manages forward and reverse tunnels.

    This class implements the TunnelService server interface and provides
    methods for managing both forward tunnels (client -> server RPCs) and
    reverse tunnels (server -> client RPCs).

    Example:
        handler = TunnelServiceHandler()

        # Register services for forward tunnels
        FooServiceServicer_to_server(foo_impl, handler)

        # Register with gRPC server
        server = grpc.aio.server()
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # For reverse tunnels, get a channel to send RPCs to clients
        reverse_channel = handler.as_channel()
        stub = MyServiceStub(reverse_channel)
        await stub.MyMethod(request)
    """

    def __init__(self, options: Optional[TunnelServiceHandlerOptions] = None):
        """Initialize the tunnel service handler.

        Args:
            options: Optional configuration options
        """
        self._options = options or TunnelServiceHandlerOptions()

        # Create tunnel server for forward tunnels
        tunnel_opts = TunnelOptions(
            disable_flow_control=self._options.disable_flow_control
        )
        self._tunnel_server = TunnelServer(
            options=tunnel_opts,
            interceptors=self._options.server_interceptors,
        )

        # Reverse tunnel management
        self._reverse_channels = ReverseChannels()
        self._reverse_by_key: Dict[Any, ReverseChannels] = {}
        self._reverse_lock = asyncio.Lock()
        self._stopping = False

    def register_method(
        self,
        method_name: str,
        handler: Callable[..., Any],
        is_client_stream: bool = False,
        is_server_stream: bool = False,
    ) -> None:
        """Register a method handler for forward tunnels.

        Args:
            method_name: Full method name like "myservice.MyService/MyMethod"
            handler: Async callable that implements the method
            is_client_stream: Whether this is a client streaming method
            is_server_stream: Whether this is a server streaming method
        """
        self._tunnel_server.register_method(
            method_name, handler, is_client_stream, is_server_stream
        )

    def register_service(self, servicer: Any) -> None:
        """Register all methods from a service implementation for forward tunnels.

        This method automatically discovers and registers all methods from a
        service implementation by introspecting the generated *Servicer base class.

        The servicer MUST extend a generated *Servicer base class (e.g., EdgeServiceServicer,
        EchoServiceServicer) for auto-detection to work. This follows the standard gRPC
        pattern used in Go, Java, and C++.

        Args:
            servicer: The service implementation instance that extends a *Servicer base class

        Example:
            # Define your service by extending the generated servicer
            class EchoServiceImpl(echo_pb2_grpc.EchoServiceServicer):
                async def Echo(self, request, context):
                    return echo_pb2.EchoResponse(message=f"Echo: {request.message}")

            # Register - service name and method signatures are auto-detected
            handler.register_service(EchoServiceImpl())

        Raises:
            ValueError: If servicer doesn't extend a *Servicer base class or
                       if service metadata cannot be extracted
        """
        # Auto-detect service metadata from the servicer's base class
        service_name, method_descriptors = _extract_service_metadata(servicer)

        # Get all methods from the servicer
        for method_name in dir(servicer):
            # Skip private/magic methods
            if method_name.startswith("_"):
                continue

            method = getattr(servicer, method_name)

            # Check if it's a callable method
            if not callable(method):
                continue

            # Get method type info from detected descriptors
            if method_name not in method_descriptors:
                # Method not in the service definition, skip it
                continue

            # Check if method is async or sync
            is_async_method = inspect.iscoroutinefunction(method)

            descriptor = method_descriptors[method_name]
            is_client_stream = descriptor.get("is_client_stream", False)
            is_server_stream = descriptor.get("is_server_stream", False)
            request_deserializer = descriptor.get("request_deserializer")
            response_serializer = descriptor.get("response_serializer")

            # Create a wrapper that handles serialization/deserialization
            # The tunnel works with raw bytes, but gRPC methods work with protobuf objects
            if is_client_stream or is_server_stream:
                # For streaming methods, the handler signature is different
                # We'll handle this later if needed
                handler = method
            else:
                # For unary methods, wrap with deserializer/serializer
                # Use a factory function to avoid closure issues
                if is_async_method:
                    # Async method - call directly
                    def make_async_wrapper(user_method, req_deser, resp_ser):
                        async def wrapped_handler(request_bytes: bytes, context: Any) -> bytes:
                            # Deserialize request
                            request = req_deser(request_bytes) if req_deser else request_bytes
                            # Call user method (async)
                            response = await user_method(request, context)
                            # Serialize response
                            return resp_ser(response) if resp_ser else response
                        return wrapped_handler
                    handler = make_async_wrapper(method, request_deserializer, response_serializer)
                else:
                    # Sync method - run in thread pool to avoid blocking event loop
                    def make_sync_wrapper(user_method, req_deser, resp_ser):
                        async def wrapped_handler(request_bytes: bytes, context: Any) -> bytes:
                            # Deserialize request
                            request = req_deser(request_bytes) if req_deser else request_bytes
                            # Call user method (sync) in thread pool
                            response = await asyncio.to_thread(user_method, request, context)
                            # Serialize response
                            return resp_ser(response) if resp_ser else response
                        return wrapped_handler
                    handler = make_sync_wrapper(method, request_deserializer, response_serializer)

            # Register the method
            full_method_name = f"{service_name}/{method_name}"
            self.register_method(
                full_method_name,
                handler,
                is_client_stream=is_client_stream,
                is_server_stream=is_server_stream,
            )

    def service(self) -> "TunnelServiceImpl":
        """Get the TunnelService implementation to register with a gRPC server.

        Returns:
            A TunnelServiceServicer implementation
        """
        return TunnelServiceImpl(self)

    def initiate_shutdown(self) -> None:
        """Begin graceful shutdown, preventing new operations."""
        self._stopping = True
        self._tunnel_server.shutdown()

    async def all_reverse_tunnels(self) -> List[TunnelChannel]:
        """Get all currently active reverse tunnel channels.

        Returns:
            List of TunnelChannel instances
        """
        return await self._reverse_channels.all_channels()

    def as_channel(self) -> "ReverseChannel":
        """Get a channel for sending RPCs to all reverse tunnel clients.

        The returned channel will round-robin across all available reverse
        tunnels.

        Returns:
            A channel that can be used to create stubs and send RPCs

        Raises:
            RuntimeError: If reverse tunnels are disabled
        """
        if self._options.no_reverse_tunnels:
            raise RuntimeError("reverse tunnels not supported")
        return ReverseChannel(self._reverse_channels)

    def key_as_channel(self, key: Any) -> "ReverseChannel":
        """Get a channel for sending RPCs to reverse tunnels with a specific affinity key.

        Args:
            key: The affinity key to match

        Returns:
            A channel that round-robins across matching reverse tunnels

        Raises:
            RuntimeError: If reverse tunnels are disabled
        """
        if self._options.no_reverse_tunnels:
            raise RuntimeError("reverse tunnels not supported")

        # Get or create channels for this key
        if key not in self._reverse_by_key:
            self._reverse_by_key[key] = ReverseChannels()

        return ReverseChannel(self._reverse_by_key[key])

    async def _open_tunnel(self, stream: Any) -> None:
        """Handle an OpenTunnel request (forward tunnel).

        Args:
            stream: The bidirectional gRPC stream
        """
        # Check if we have any handlers registered
        if not self._tunnel_server._handlers:
            raise grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNIMPLEMENTED,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details="forward tunnels not supported",
            )

        # Send negotiation header
        await stream.send_initial_metadata((("grpctunnel-negotiate", "on"),))

        # Check if client supports settings
        metadata = dict(stream.invocation_metadata())
        client_accepts_settings = metadata.get("grpctunnel-negotiate") == "on"

        # Serve the tunnel
        await self._tunnel_server.serve_tunnel(stream, client_accepts_settings)

    async def _open_reverse_tunnel(self, stream: Any, context: Any) -> None:
        """Handle an OpenReverseTunnel request (reverse tunnel).

        Args:
            stream: Iterator of ServerToClient messages (from client acting as server)
            context: gRPC service context
        """
        if self._options.no_reverse_tunnels:
            raise grpc.aio.AioRpcError(
                code=grpc.StatusCode.UNIMPLEMENTED,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details="reverse tunnels not supported",
            )

        # Send negotiation header
        await context.send_initial_metadata((("grpctunnel-negotiate", "on"),))

        # Check if client supports settings
        metadata = dict(context.invocation_metadata())
        client_accepts_settings = metadata.get("grpctunnel-negotiate") == "on"

        # Create a reverse tunnel channel wrapper
        # For reverse tunnels, the message directions are swapped:
        # - Client sends ServerToClient (acting as server)
        # - Server sends ClientToServer (acting as client)
        class ReverseTunnelStreamAdapter:
            """Adapts reverse tunnel stream for use as TunnelChannel."""

            def __init__(self, request_iterator, context):
                self._request_iterator = request_iterator
                self._context = context
                self._write_queue = asyncio.Queue()
                self._closed = False
                self._read_lock = asyncio.Lock()
                self._write_lock = asyncio.Lock()

            async def read(self):
                """Read ServerToClient message from client."""
                async with self._read_lock:
                    try:
                        msg = await self._request_iterator.__anext__()
                        return msg
                    except StopAsyncIteration:
                        return None

            async def write(self, msg):
                """Write ClientToServer message to client."""
                async with self._write_lock:
                    if not self._closed:
                        await self._write_queue.put(msg)

            def invocation_metadata(self):
                """Get invocation metadata."""
                return self._context.invocation_metadata()

            def close(self):
                """Mark as closed."""
                self._closed = True
                try:
                    self._write_queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass

        adapter = ReverseTunnelStreamAdapter(stream, context)

        # Create a ReverseTunnelChannel that can send RPCs to the client
        # For reverse tunnels, message directions are inverted:
        # - Server sends ClientToServer messages (acting as client)
        # - Server receives ServerToClient messages (from client acting as server)
        tunnel_opts = TunnelOptions(
            disable_flow_control=self._options.disable_flow_control
        )
        tunnel_channel = ReverseTunnelChannel(
            stream_adapter=adapter,
            options=tunnel_opts,
            client_will_send_settings=client_accepts_settings,
        )

        # Track this reverse tunnel
        await self._reverse_channels.add(tunnel_channel)  # type: ignore

        # Compute affinity key if provided
        key = None
        if self._options.affinity_key:
            key = self._options.affinity_key(tunnel_channel)  # type: ignore

        if key is not None:
            if key not in self._reverse_by_key:
                self._reverse_by_key[key] = ReverseChannels()
            await self._reverse_by_key[key].add(tunnel_channel)  # type: ignore

        # Call open callback
        if self._options.on_reverse_tunnel_open:
            self._options.on_reverse_tunnel_open(tunnel_channel)  # type: ignore

        try:
            # Yield messages from the write queue
            while not adapter._closed:
                try:
                    msg = await asyncio.wait_for(
                        adapter._write_queue.get(), timeout=5.0
                    )
                    if msg is None:
                        break
                    yield msg
                except asyncio.TimeoutError:
                    continue
        finally:
            # Remove from tracking
            await self._reverse_channels.remove(tunnel_channel)  # type: ignore
            if key is not None and key in self._reverse_by_key:
                await self._reverse_by_key[key].remove(tunnel_channel)  # type: ignore

            # Call close callback
            if self._options.on_reverse_tunnel_close:
                self._options.on_reverse_tunnel_close(tunnel_channel)  # type: ignore

            # Close the tunnel channel to stop its internal send/recv loops
            await tunnel_channel.close_async()

            adapter.close()


class TunnelServiceImpl(TunnelServiceServicer):
    """Implementation of the TunnelService gRPC service."""

    def __init__(self, handler: TunnelServiceHandler):
        """Initialize the service implementation.

        Args:
            handler: The TunnelServiceHandler that manages tunnels
        """
        self._handler = handler

    async def OpenTunnel(self, request_iterator: Any, context: Any) -> Any:
        """Handle OpenTunnel RPC (forward tunnel).

        Args:
            request_iterator: Iterator of ClientToServer messages
            context: gRPC context

        Yields:
            ServerToClient messages
        """
        # Create a wrapper that provides the bidirectional stream interface
        class BidirectionalStreamWrapper:
            """Wrapper to adapt gRPC servicer interface to bidirectional stream."""

            def __init__(self, request_iterator, context):
                self._request_iterator = request_iterator
                self._context = context
                self._write_queue = asyncio.Queue()
                self._closed = False

            def __aiter__(self):
                """Support async iteration for reading."""
                return self

            async def write(self, message):
                """Write a message to the client."""
                if not self._closed:
                    await self._write_queue.put(message)

            async def read(self):
                """Read next message from request_iterator."""
                try:
                    msg = await self._request_iterator.__anext__()
                    return msg
                except StopAsyncIteration:
                    return None

            async def __anext__(self):
                """Read next message for async iteration."""
                msg = await self.read()
                if msg is None:
                    raise StopAsyncIteration
                return msg

            def close(self):
                """Mark the wrapper as closed."""
                self._closed = True
                try:
                    self._write_queue.put_nowait(None)
                except asyncio.QueueFull:
                    pass

            def invocation_metadata(self):
                """Get invocation metadata."""
                return self._context.invocation_metadata()

            async def send_initial_metadata(self, metadata):
                """Send initial metadata."""
                await self._context.send_initial_metadata(metadata)

        wrapper = BidirectionalStreamWrapper(request_iterator, context)

        # Create a task to serve the tunnel
        async def serve():
            try:
                await self._handler._open_tunnel(wrapper)
            except Exception as e:
                import traceback

                traceback.print_exc()
            finally:
                wrapper.close()

        serve_task = asyncio.create_task(serve())

        # Give the serve task a moment to start
        await asyncio.sleep(0.01)

        try:
            # Yield messages from the queue
            while not wrapper._closed:
                try:
                    msg = await asyncio.wait_for(
                        wrapper._write_queue.get(), timeout=5.0
                    )
                    if msg is None:  # Sentinel value
                        break
                    yield msg
                except asyncio.TimeoutError:
                    if serve_task.done():
                        break
                    continue
        finally:
            if not serve_task.done():
                try:
                    await asyncio.wait_for(serve_task, timeout=10.0)
                except asyncio.TimeoutError:
                    serve_task.cancel()
                    try:
                        await serve_task
                    except asyncio.CancelledError:
                        pass

    async def OpenReverseTunnel(self, request_iterator: Any, context: Any) -> Any:
        """Handle OpenReverseTunnel RPC (reverse tunnel).

        Args:
            request_iterator: Iterator of ServerToClient messages
            context: gRPC context

        Yields:
            ClientToServer messages
        """
        async for msg in self._handler._open_reverse_tunnel(request_iterator, context):
            yield msg


class ReverseChannel:
    """A channel that round-robins RPCs across reverse tunnel connections.

    This implements a subset of the grpc.Channel interface for sending
    RPCs back to clients over reverse tunnels.
    """

    def __init__(self, channels: ReverseChannels):
        """Initialize the reverse channel.

        Args:
            channels: The ReverseChannels collection to use
        """
        self._channels = channels

    def unary_unary(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> Any:
        """Create a unary-unary RPC method."""

        async def _call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            channel = await self._channels.pick()
            if channel is None:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNAVAILABLE,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="no reverse tunnels available",
                )

            # The picked channel is a ReverseTunnelChannel
            # Use its unary_unary method to create and invoke the RPC
            call = channel.unary_unary(method, request_serializer, response_deserializer)
            return await call(request, timeout=timeout, metadata=metadata, credentials=credentials)

        return _call

    def unary_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> Any:
        """Create a unary-stream RPC method."""

        async def _call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            channel = await self._channels.pick()
            if channel is None:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNAVAILABLE,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="no reverse tunnels available",
                )

            call = channel.unary_stream(method, request_serializer, response_deserializer)
            return await call(request, timeout=timeout, metadata=metadata, credentials=credentials)

        return _call

    def stream_unary(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> Any:
        """Create a stream-unary RPC method."""

        async def _call(
            request_iterator: Optional[Any] = None,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            channel = await self._channels.pick()
            if channel is None:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNAVAILABLE,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="no reverse tunnels available",
                )

            call = channel.stream_unary(method, request_serializer, response_deserializer)
            return await call(request_iterator=request_iterator, timeout=timeout, metadata=metadata, credentials=credentials)

        return _call

    def stream_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> Any:
        """Create a stream-stream (bidirectional) RPC method."""

        async def _call(
            request_iterator: Optional[Any] = None,
            timeout: Optional[float] = None,
            metadata: Optional[grpc.aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            channel = await self._channels.pick()
            if channel is None:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNAVAILABLE,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="no reverse tunnels available",
                )

            call = channel.stream_stream(method, request_serializer, response_deserializer)
            return await call(request_iterator=request_iterator, timeout=timeout, metadata=metadata, credentials=credentials)

        return _call

    def ready(self) -> bool:
        """Check if any reverse tunnels are available."""
        return self._channels.ready()

    async def wait_for_ready(self, timeout: Optional[float] = None) -> bool:
        """Wait for at least one reverse tunnel to be available."""
        return await self._channels.wait_for_ready(timeout)
