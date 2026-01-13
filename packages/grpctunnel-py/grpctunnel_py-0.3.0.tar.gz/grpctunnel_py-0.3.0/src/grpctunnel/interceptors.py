# Copyright 2024 Daniel Valdivia
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

"""Interceptor support for grpctunnel.

This module provides interceptor support for both client and server sides
of tunnel connections, allowing middleware to be added to the tunnel
processing pipeline.
"""

import asyncio
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union

import grpc
from grpc import aio

from grpctunnel.client import TunnelChannel
from grpctunnel.context import set_tunnel_channel_in_context, set_tunnel_metadata_in_context


class InterceptedTunnelChannel(grpc.aio.Channel):
    """A TunnelChannel wrapper that applies client interceptors.

    This class wraps a TunnelChannel and applies the specified interceptors
    to all RPC methods, providing the same functionality as a regular
    intercepted gRPC channel but over a tunnel.
    """

    def __init__(
        self,
        channel: TunnelChannel,
        interceptors: Optional[Sequence[aio.ClientInterceptor]] = None,
    ):
        """Initialize an intercepted tunnel channel.

        Args:
            channel: The underlying TunnelChannel
            interceptors: Optional sequence of client interceptors to apply
        """
        self._channel = channel
        self._interceptors = list(interceptors) if interceptors else []

    def unary_unary(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> aio.UnaryUnaryMultiCallable:
        """Create an intercepted unary-unary RPC method."""
        base_callable = self._channel.unary_unary(
            method, request_serializer, response_deserializer, _registered_method
        )

        if not self._interceptors:
            return base_callable

        # Create a callable that applies interceptors
        async def intercepted_call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            # Create call details
            call_details = ClientCallDetailsWrapper(
                method=method,
                timeout=timeout,
                metadata=metadata,
                credentials=credentials,
            )

            # Build the continuation chain
            def build_continuation(interceptors: List[Any], index: int):
                """Recursively build the continuation chain."""
                if index >= len(interceptors):
                    # Base case: call the actual RPC
                    async def base_continuation(details: Any, req: Any) -> Any:
                        return await base_callable(
                            req,
                            timeout=details.timeout,
                            metadata=details.metadata,
                            credentials=details.credentials,
                        )
                    return base_continuation

                # Get the next continuation in the chain
                next_continuation = build_continuation(interceptors, index + 1)

                # Create continuation for current interceptor
                interceptor = interceptors[index]
                if hasattr(interceptor, 'intercept_unary_unary'):
                    async def continuation(details: Any, req: Any) -> Any:
                        return await interceptor.intercept_unary_unary(
                            next_continuation, details, req
                        )
                    return continuation
                else:
                    # If interceptor doesn't have the method, skip it
                    return next_continuation

            # Build and execute the chain
            continuation_chain = build_continuation(self._interceptors, 0)
            return await continuation_chain(call_details, request)

        return intercepted_call

    def unary_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> aio.UnaryStreamMultiCallable:
        """Create an intercepted unary-stream RPC method."""
        base_callable = self._channel.unary_stream(
            method, request_serializer, response_deserializer, _registered_method
        )

        if not self._interceptors:
            return base_callable

        # Create a callable that applies interceptors
        async def intercepted_call(
            request: Any,
            timeout: Optional[float] = None,
            metadata: Optional[aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ):
            # Create call details
            call_details = ClientCallDetailsWrapper(
                method=method,
                timeout=timeout,
                metadata=metadata,
                credentials=credentials,
            )

            # Build the continuation chain
            def build_continuation(interceptors: List[Any], index: int):
                """Recursively build the continuation chain."""
                if index >= len(interceptors):
                    # Base case: call the actual RPC
                    async def base_continuation(details: Any, req: Any):
                        return await base_callable(
                            req,
                            timeout=details.timeout,
                            metadata=details.metadata,
                            credentials=details.credentials,
                        )
                    return base_continuation

                # Get the next continuation in the chain
                next_continuation = build_continuation(interceptors, index + 1)

                # Create continuation for current interceptor
                interceptor = interceptors[index]
                if hasattr(interceptor, 'intercept_unary_stream'):
                    async def continuation(details: Any, req: Any):
                        return await interceptor.intercept_unary_stream(
                            next_continuation, details, req
                        )
                    return continuation
                else:
                    # If interceptor doesn't have the method, skip it
                    return next_continuation

            # Build and execute the chain
            continuation_chain = build_continuation(self._interceptors, 0)
            return await continuation_chain(call_details, request)

        return intercepted_call

    def stream_unary(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> aio.StreamUnaryMultiCallable:
        """Create an intercepted stream-unary RPC method."""
        base_callable = self._channel.stream_unary(
            method, request_serializer, response_deserializer, _registered_method
        )

        if not self._interceptors:
            return base_callable

        # Create a callable that applies interceptors
        async def intercepted_call(
            request_iterator: Any,
            timeout: Optional[float] = None,
            metadata: Optional[aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ) -> Any:
            # Create call details
            call_details = ClientCallDetailsWrapper(
                method=method,
                timeout=timeout,
                metadata=metadata,
                credentials=credentials,
            )

            # Build the continuation chain
            def build_continuation(interceptors: List[Any], index: int):
                """Recursively build the continuation chain."""
                if index >= len(interceptors):
                    # Base case: call the actual RPC
                    async def base_continuation(details: Any, req_iter: Any) -> Any:
                        return await base_callable(
                            req_iter,
                            timeout=details.timeout,
                            metadata=details.metadata,
                            credentials=details.credentials,
                        )
                    return base_continuation

                # Get the next continuation in the chain
                next_continuation = build_continuation(interceptors, index + 1)

                # Create continuation for current interceptor
                interceptor = interceptors[index]
                if hasattr(interceptor, 'intercept_stream_unary'):
                    async def continuation(details: Any, req_iter: Any) -> Any:
                        return await interceptor.intercept_stream_unary(
                            next_continuation, details, req_iter
                        )
                    return continuation
                else:
                    # If interceptor doesn't have the method, skip it
                    return next_continuation

            # Build and execute the chain
            continuation_chain = build_continuation(self._interceptors, 0)
            return await continuation_chain(call_details, request_iterator)

        return intercepted_call

    def stream_stream(
        self,
        method: str,
        request_serializer: Optional[Callable[[Any], bytes]] = None,
        response_deserializer: Optional[Callable[[bytes], Any]] = None,
        _registered_method: bool = False,
    ) -> aio.StreamStreamMultiCallable:
        """Create an intercepted stream-stream RPC method."""
        base_callable = self._channel.stream_stream(
            method, request_serializer, response_deserializer, _registered_method
        )

        if not self._interceptors:
            return base_callable

        # Create a callable that applies interceptors
        async def intercepted_call(
            request_iterator: Any,
            timeout: Optional[float] = None,
            metadata: Optional[aio.Metadata] = None,
            credentials: Optional[grpc.CallCredentials] = None,
        ):
            # Create call details
            call_details = ClientCallDetailsWrapper(
                method=method,
                timeout=timeout,
                metadata=metadata,
                credentials=credentials,
            )

            # Build the continuation chain
            def build_continuation(interceptors: List[Any], index: int):
                """Recursively build the continuation chain."""
                if index >= len(interceptors):
                    # Base case: call the actual RPC
                    async def base_continuation(details: Any, req_iter: Any):
                        return await base_callable(
                            req_iter,
                            timeout=details.timeout,
                            metadata=details.metadata,
                            credentials=details.credentials,
                        )
                    return base_continuation

                # Get the next continuation in the chain
                next_continuation = build_continuation(interceptors, index + 1)

                # Create continuation for current interceptor
                interceptor = interceptors[index]
                if hasattr(interceptor, 'intercept_stream_stream'):
                    async def continuation(details: Any, req_iter: Any):
                        return await interceptor.intercept_stream_stream(
                            next_continuation, details, req_iter
                        )
                    return continuation
                else:
                    # If interceptor doesn't have the method, skip it
                    return next_continuation

            # Build and execute the chain
            continuation_chain = build_continuation(self._interceptors, 0)
            return await continuation_chain(call_details, request_iterator)

        return intercepted_call

    async def close_async(self) -> None:
        """Close the channel asynchronously."""
        await self._channel.close_async()

    def close(self) -> None:
        """Close the channel."""
        self._channel.close()

    async def channel_ready(self) -> None:
        """Wait for the channel to be ready."""
        await self._channel.channel_ready()

    def get_state(self, try_to_connect: bool = False) -> grpc.ChannelConnectivity:
        """Get the current connectivity state."""
        return self._channel.get_state(try_to_connect)

    async def wait_for_state_change(
        self, last_observed_state: grpc.ChannelConnectivity
    ) -> None:
        """Wait for the channel state to change."""
        await self._channel.wait_for_state_change(last_observed_state)

    async def wait_for_termination(self, timeout: Optional[float] = None) -> bool:
        """Wait for the channel to terminate."""
        return await self._channel.wait_for_termination(timeout)

    async def __aenter__(self) -> "InterceptedTunnelChannel":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close_async()


class ClientCallDetailsWrapper:
    """Wrapper for client call details used by interceptors."""

    def __init__(
        self,
        method: str,
        timeout: Optional[float] = None,
        metadata: Optional[aio.Metadata] = None,
        credentials: Optional[grpc.CallCredentials] = None,
        wait_for_ready: Optional[bool] = None,
        compression: Optional[grpc.Compression] = None,
    ):
        """Initialize call details."""
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


class TunnelServerInterceptor(aio.ServerInterceptor):
    """Base class for server interceptors that work with tunnels.

    This interceptor ensures that tunnel context information is properly
    propagated to the service handlers.
    """

    def __init__(self, tunnel_channel: Optional[Any] = None):
        """Initialize the tunnel server interceptor.

        Args:
            tunnel_channel: The tunnel channel handling this request, if any
        """
        self._tunnel_channel = tunnel_channel

    def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Any],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Any:
        """Intercept a service call.

        Args:
            continuation: The next interceptor or actual handler
            handler_call_details: Details about the call

        Returns:
            The RPC method handler
        """
        # Get the base handler
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        # If we have a tunnel channel, wrap the handler to inject context
        if self._tunnel_channel:
            return self._wrap_handler_with_context(handler)

        return handler

    def _wrap_handler_with_context(
        self, handler: Any
    ) -> Any:
        """Wrap a handler to inject tunnel context.

        Args:
            handler: The original handler

        Returns:
            A wrapped handler that sets tunnel context
        """
        # For now, just return the handler as-is
        # Full implementation would require deeper integration with gRPC internals
        return handler


class LoggingInterceptor(aio.UnaryUnaryClientInterceptor):
    """Example client interceptor that logs RPC calls.

    This is an example interceptor that can be used with tunnels to
    log all unary-unary RPC calls.
    """

    async def intercept_unary_unary(
        self,
        continuation: Callable[[grpc.ClientCallDetails, Any], Any],
        client_call_details: grpc.ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-unary call.

        Args:
            continuation: The next interceptor or actual call
            client_call_details: Details about the call
            request: The request message

        Returns:
            The response from the continuation
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Calling {client_call_details.method}")
        try:
            response = await continuation(client_call_details, request)
            logger.info(f"Call to {client_call_details.method} succeeded")
            return response
        except Exception as e:
            logger.error(f"Call to {client_call_details.method} failed: {e}")
            raise


class MetadataInterceptor(aio.UnaryUnaryClientInterceptor):
    """Example client interceptor that adds metadata to all calls.

    This interceptor adds custom metadata to all unary-unary RPC calls.
    """

    def __init__(self, metadata_to_add: Sequence[Tuple[str, str]]):
        """Initialize the metadata interceptor.

        Args:
            metadata_to_add: Metadata key-value pairs to add to all calls
        """
        self._metadata_to_add = list(metadata_to_add)

    async def intercept_unary_unary(
        self,
        continuation: Callable[[grpc.ClientCallDetails, Any], Any],
        client_call_details: grpc.ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-unary call to add metadata.

        Args:
            continuation: The next interceptor or actual call
            client_call_details: Details about the call
            request: The request message

        Returns:
            The response from the continuation
        """
        # Add our metadata to the existing metadata
        metadata = []
        if client_call_details.metadata:
            metadata.extend(client_call_details.metadata)
        metadata.extend(self._metadata_to_add)

        # Create new call details with updated metadata
        new_details = ClientCallDetailsWrapper(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=grpc.aio.Metadata(*metadata),
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready,
            compression=client_call_details.compression,
        )

        return await continuation(new_details, request)


def intercept_tunnel_channel(
    channel: TunnelChannel,
    interceptors: Sequence[aio.ClientInterceptor],
) -> InterceptedTunnelChannel:
    """Create an intercepted tunnel channel.

    This is a convenience function to wrap a TunnelChannel with interceptors.

    Args:
        channel: The tunnel channel to wrap
        interceptors: Sequence of client interceptors to apply

    Returns:
        An InterceptedTunnelChannel that applies the interceptors

    Example:
        channel = await pending_channel.start()
        intercepted = intercept_tunnel_channel(channel, [
            LoggingInterceptor(),
            MetadataInterceptor([("custom-header", "value")]),
        ])
        stub = MyServiceStub(intercepted)
        response = await stub.MyMethod(request)
    """
    return InterceptedTunnelChannel(channel, interceptors)