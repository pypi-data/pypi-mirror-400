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

"""Context utilities for grpctunnel.

This module provides utilities for working with tunnel channels in request contexts,
similar to the Go implementation's context functions.
"""

from typing import Any, Dict, Optional, Tuple

import grpc

# Context key for storing tunnel channel reference
_TUNNEL_CHANNEL_KEY = "grpctunnel.tunnel_channel"
_TUNNEL_METADATA_KEY = "grpctunnel.tunnel_metadata"


def tunnel_channel_from_context(context: grpc.ServicerContext) -> Optional[Any]:
    """Extract the TunnelChannel from a request context.

    This function returns the TunnelChannel that is handling the given request,
    or None if the request is not being handled by a tunnel channel.

    This is useful in server-side handlers to determine if a request came
    through a tunnel and to get information about that tunnel.

    Args:
        context: The gRPC servicer context

    Returns:
        The TunnelChannel handling this request, or None if not tunneled

    Example:
        async def my_handler(request, context):
            tunnel = tunnel_channel_from_context(context)
            if tunnel:
                # Request came through a tunnel
                print(f"Request via tunnel: {tunnel}")
    """
    if not hasattr(context, '_tunnel_channel'):
        return None
    return getattr(context, '_tunnel_channel', None)


def with_tunnel_channel(channel: Any) -> Dict[str, Any]:
    """Create context values with a specific TunnelChannel.

    This function creates a dictionary of context values that can be used
    to associate a specific TunnelChannel with outgoing RPCs.

    Args:
        channel: The TunnelChannel to associate with the context

    Returns:
        A dictionary of context values to be used with RPC calls

    Example:
        channel = await pending_channel.start()
        context_values = with_tunnel_channel(channel)
        # Use context_values in RPC calls
    """
    return {_TUNNEL_CHANNEL_KEY: channel}


def tunnel_metadata_from_incoming_context(
    context: grpc.ServicerContext
) -> Optional[grpc.aio.Metadata]:
    """Get tunnel metadata from incoming request context (server-side).

    This provides server-side access to the request metadata that was used
    to open the tunnel. This is useful for server interceptors that need
    to inspect tunnel-specific metadata.

    Args:
        context: The gRPC servicer context

    Returns:
        The metadata used to open the tunnel, or None if not tunneled
    """
    if not hasattr(context, '_tunnel_metadata'):
        return None
    metadata = getattr(context, '_tunnel_metadata', None)
    if metadata is None:
        return None
    # grpc.aio.Metadata expects each key-value pair as a separate argument
    return grpc.aio.Metadata(*metadata) if isinstance(metadata, list) else metadata


def tunnel_metadata_from_outgoing_context(
    metadata: Optional[grpc.aio.Metadata] = None
) -> Optional[grpc.aio.Metadata]:
    """Get tunnel metadata from outgoing request context (client-side).

    This provides client-side access to the request metadata that will be
    used to open a forward tunnel. This is useful for client interceptors
    that need to inspect or modify tunnel-specific metadata.

    Args:
        metadata: The outgoing metadata

    Returns:
        The metadata that will be used to open the tunnel
    """
    if metadata is None:
        return None

    # Filter for tunnel-specific metadata
    tunnel_metadata = []
    # grpc.aio.Metadata can be iterated over as (key, value) pairs
    for key, value in metadata:
        if key.startswith('grpctunnel-'):
            tunnel_metadata.append((key, value))

    return grpc.aio.Metadata(*tunnel_metadata) if tunnel_metadata else None


def set_tunnel_channel_in_context(
    context: grpc.ServicerContext, channel: Any
) -> None:
    """Internal helper to set tunnel channel in a servicer context.

    This is used internally by the tunnel implementation to associate
    a tunnel channel with incoming requests.

    Args:
        context: The gRPC servicer context
        channel: The TunnelChannel handling this request
    """
    setattr(context, '_tunnel_channel', channel)


def set_tunnel_metadata_in_context(
    context: grpc.ServicerContext,
    metadata: Optional[grpc.aio.Metadata]
) -> None:
    """Internal helper to set tunnel metadata in a servicer context.

    This is used internally by the tunnel implementation to store
    the metadata used to open the tunnel.

    Args:
        context: The gRPC servicer context
        metadata: The metadata used to open the tunnel
    """
    if metadata is not None:
        setattr(context, '_tunnel_metadata', list(metadata) if metadata else [])