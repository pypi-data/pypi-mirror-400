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

"""Reverse tunnel server implementation.

This module provides the ReverseTunnelServer, which allows a gRPC client to
act as a server for reverse tunnels. The server can then send RPC requests
back to the client over the reverse tunnel.
"""

import asyncio
import importlib
import inspect
from enum import IntEnum
from typing import Any, Callable, Dict, Optional, Tuple

import grpc

from grpctunnel.options import TunnelOptions
from grpctunnel.proto.v1 import TunnelServiceStub
from grpctunnel.server import TunnelServer


class ServerState(IntEnum):
    """State of the reverse tunnel server."""

    ACTIVE = 0
    CLOSING = 1
    CLOSED = 2


def _extract_service_metadata(
    servicer: Any,
) -> Tuple[str, Dict[str, Dict[str, Any]]]:
    """Extract service name and method descriptors from a servicer instance.

    This function requires that the servicer extends a generated *Servicer base class
    (e.g., EdgeServiceServicer). It finds the base class, locates the corresponding
    add_*Servicer_to_server function, and extracts all service metadata.

    Args:
        servicer: The service implementation instance that extends a *Servicer base class

    Returns:
        Tuple of (service_name, method_descriptors) where:
        - service_name: Full service name like "package.Service"
        - method_descriptors: Dict mapping method names to metadata including:
          - is_client_stream: bool
          - is_server_stream: bool
          - request_deserializer: Callable[[bytes], Message]
          - response_serializer: Callable[[Message], bytes]

    Raises:
        ValueError: If servicer doesn't extend a *Servicer base class or metadata cannot be extracted
    """
    # Find the servicer base class (should end with "Servicer")
    servicer_class = servicer.__class__
    servicer_base = None

    # Skip the servicer's own class (index 0) to find the generated base class
    # This prevents issues when user's class has the same name as the base class
    for base in inspect.getmro(servicer_class)[1:]:
        if base.__name__.endswith("Servicer") and base.__name__ != "Servicer":
            # Found a base class like EdgeServiceServicer
            servicer_base = base
            break

    if servicer_base is None:
        raise ValueError(
            f"Servicer class '{servicer_class.__name__}' must extend a generated "
            f"*Servicer base class (e.g., EdgeServiceServicer, EchoServiceServicer). "
            f"This is required for auto-detection of service metadata. "
            f"Make sure your servicer extends a class from the generated *_pb2_grpc module."
        )

    servicer_base_name = servicer_base.__name__
    servicer_module_name = servicer_base.__module__

    # Import the module containing the servicer base class
    try:
        servicer_module = importlib.import_module(servicer_module_name)
    except ImportError as e:
        raise ValueError(
            f"Cannot import module '{servicer_module_name}' for servicer base class "
            f"'{servicer_base_name}': {e}"
        ) from e

    # Find the add_*Servicer_to_server function
    add_function_name = f"add_{servicer_base_name}_to_server"
    add_function = getattr(servicer_module, add_function_name, None)

    if add_function is None:
        raise ValueError(
            f"Cannot find '{add_function_name}' function in module '{servicer_module_name}'. "
            f"The generated protobuf code may be incomplete or corrupted."
        )

    # Create a mock server to capture the service registration
    class MockServer:
        def __init__(self) -> None:
            self.service_name: Optional[str] = None
            self.method_handlers: Dict[str, Any] = {}

        def add_generic_rpc_handlers(self, handlers: Any) -> None:
            # Extract service name from the generic handler
            for handler in handlers:
                if hasattr(handler, "service_name"):
                    self.service_name = handler.service_name()

        def add_registered_method_handlers(
            self, service_name: str, method_handlers: Dict[str, Any]
        ) -> None:
            # Called with service name and method handlers dict
            if not self.service_name:
                self.service_name = service_name
            self.method_handlers = method_handlers

    # Call the add function with our mock server
    mock_server = MockServer()
    try:
        add_function(servicer, mock_server)
    except Exception as e:
        raise ValueError(
            f"Error calling '{add_function_name}': {e}. "
            f"Make sure the servicer implements all required methods from {servicer_base_name}."
        ) from e

    if not mock_server.service_name:
        raise ValueError(
            f"Could not extract service name from '{add_function_name}'. "
            f"The generated code may be incompatible with this version of grpctunnel."
        )

    # Extract method descriptors from the method handlers
    method_descriptors: Dict[str, Dict[str, Any]] = {}

    for method_name, handler in mock_server.method_handlers.items():
        # Determine streaming type from the handler
        # Handlers are created by grpc.*_rpc_method_handler functions
        is_client_stream = False
        is_server_stream = False

        # Check if handler has streaming attributes
        if hasattr(handler, "request_streaming"):
            is_client_stream = handler.request_streaming
        if hasattr(handler, "response_streaming"):
            is_server_stream = handler.response_streaming

        # Extract deserializer and serializer functions
        request_deserializer = None
        response_serializer = None

        if hasattr(handler, "request_deserializer"):
            request_deserializer = handler.request_deserializer
        if hasattr(handler, "response_serializer"):
            response_serializer = handler.response_serializer

        method_descriptors[method_name] = {
            "is_client_stream": is_client_stream,
            "is_server_stream": is_server_stream,
            "request_deserializer": request_deserializer,
            "response_serializer": response_serializer,
        }

    return mock_server.service_name, method_descriptors


class ReverseTunnelServer:
    """A server that runs on the client side, handling requests over reverse tunnels.

    The ReverseTunnelServer allows a gRPC client to act as a server, handling
    requests sent by the gRPC server over a reverse tunnel connection.

    Example:
        stub = TunnelServiceStub(channel)
        reverse_server = ReverseTunnelServer(stub)

        # Register services
        FooServiceServicer_to_server(foo_impl, reverse_server)

        # Open reverse tunnel and serve requests
        started, err = await reverse_server.serve()
    """

    def __init__(
        self, stub: TunnelServiceStub, options: Optional[TunnelOptions] = None
    ):
        """Initialize a reverse tunnel server.

        Args:
            stub: TunnelService stub for opening reverse tunnels
            options: Optional tunnel configuration
        """
        self._stub = stub
        self._options = options or TunnelOptions()
        self._tunnel_server = TunnelServer(options=self._options)

        # State management
        self._state = ServerState.ACTIVE
        self._state_lock = asyncio.Lock()

        # Track active tunnel instances
        self._instances: Dict[Any, asyncio.Task] = {}
        self._instances_lock = asyncio.Lock()

    def register_method(
        self,
        method_name: str,
        handler: Callable[..., Any],
        is_client_stream: bool = False,
        is_server_stream: bool = False,
    ) -> None:
        """Register a method handler.

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
        """Register all methods from a service implementation.

        This method automatically discovers and registers all methods from a
        service implementation by introspecting the generated *Servicer base class.

        The servicer MUST extend a generated *Servicer base class (e.g., EdgeServiceServicer,
        EchoServiceServicer) for auto-detection to work. This follows the standard gRPC
        pattern used in Go, Java, and C++.

        Args:
            servicer: The service implementation instance that extends a *Servicer base class

        Example:
            # Define your service by extending the generated servicer
            class EdgeServiceImpl(edge_pb2_grpc.EdgeServiceServicer):
                async def GetId(self, request, context):
                    return edge_pb2.GetIdResponse(id="edge-123")

                async def GetWhatTimeItIs(self, request, context):
                    return edge_pb2.GetTimeResponse(...)

            # Register - service name and method signatures are auto-detected
            reverse_server.register_service(EdgeServiceImpl())

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

    async def serve(
        self, metadata: Optional[grpc.aio.Metadata] = None, **kwargs: Any
    ) -> tuple[bool, Optional[Exception]]:
        """Create a reverse tunnel and serve incoming requests.

        This method opens a reverse tunnel to the server and handles incoming
        RPC requests from the server. It blocks until the tunnel is closed.

        Args:
            metadata: Optional metadata for the OpenReverseTunnel call
            **kwargs: Additional call options

        Returns:
            A tuple of (started, error) where:
            - started: True if tunnel was created, False if it failed to create
            - error: None if successful, exception if tunnel ended abnormally
        """
        # Check if we're shutting down
        async with self._state_lock:
            if self._state >= ServerState.CLOSING:
                return False, Exception("server is shutting down")

        # Add negotiation header
        if metadata is None:
            metadata = grpc.aio.Metadata()
        metadata = grpc.aio.Metadata(*metadata, ("grpctunnel-negotiate", "on"))

        # Open reverse tunnel
        try:
            stream = self._stub.OpenReverseTunnel(metadata=metadata, **kwargs)
        except Exception as e:
            return False, e

        # Check response headers
        try:
            resp_metadata = await stream.initial_metadata()
        except Exception as e:
            return False, e

        # Check if server supports settings negotiation
        client_accepts_settings = False
        if resp_metadata:
            for key, value in resp_metadata:
                if key == "grpctunnel-negotiate" and value == "on":
                    client_accepts_settings = True
                    break

        # Track this instance
        current_task = asyncio.current_task()
        async with self._instances_lock:
            self._instances[stream] = current_task  # type: ignore

        try:
            # Serve the tunnel
            await self._tunnel_server.serve_tunnel(stream, client_accepts_settings)
            return True, None
        except asyncio.CancelledError:
            # Check if cancellation was due to shutdown
            async with self._state_lock:
                if self._state >= ServerState.CLOSED:
                    return True, None
                raise
        except Exception as e:
            return True, e
        finally:
            # Remove instance
            async with self._instances_lock:
                self._instances.pop(stream, None)

    async def stop(self) -> None:
        """Stop the server immediately, cancelling all active tunnels."""
        async with self._state_lock:
            if self._state == ServerState.CLOSED:
                return
            self._state = ServerState.CLOSED

        # Cancel all active instances
        async with self._instances_lock:
            tasks = list(self._instances.values())

        for task in tasks:
            if task and not task.done():
                task.cancel()

        # Wait for all to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def graceful_stop(self) -> None:
        """Stop the server gracefully, allowing existing operations to complete."""
        async with self._state_lock:
            if self._state != ServerState.ACTIVE:
                return
            self._state = ServerState.CLOSING

        # Wait for all instances to complete
        while True:
            async with self._instances_lock:
                if not self._instances:
                    break
                tasks = list(self._instances.values())

            if tasks:
                await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            else:
                break

        async with self._state_lock:
            self._state = ServerState.CLOSED
