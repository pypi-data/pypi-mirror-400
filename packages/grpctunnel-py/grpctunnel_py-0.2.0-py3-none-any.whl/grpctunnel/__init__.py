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
grpctunnel - Carry gRPC over gRPC

This library enables tunneling gRPC connections through other gRPC connections,
supporting both forward and reverse tunnels.
"""

__version__ = "0.1.0"

from grpctunnel.client import PendingChannel, TunnelChannel
from grpctunnel.context import (
    tunnel_channel_from_context,
    tunnel_metadata_from_incoming_context,
    tunnel_metadata_from_outgoing_context,
    with_tunnel_channel,
)
from grpctunnel.handler import (
    ReverseChannel,
    TunnelServiceHandler,
    TunnelServiceHandlerOptions,
)
from grpctunnel.options import (
    TunnelOptions,
    TunnelOpts,
    TunnelOption,
    TunnelOptFunc,
    with_disable_flow_control,
    apply_tunnel_options,
    normalize_options,
)
from grpctunnel.reverse import ReverseTunnelServer
from grpctunnel.server import TunnelServer

from grpctunnel.interceptors import (
    InterceptedTunnelChannel,
    LoggingInterceptor,
    MetadataInterceptor,
    intercept_tunnel_channel,
)

__all__ = [
    # Core classes
    "PendingChannel",
    "TunnelChannel",
    "TunnelServer",
    "ReverseTunnelServer",
    "TunnelServiceHandler",
    "TunnelServiceHandlerOptions",
    "ReverseChannel",
    # Options
    "TunnelOptions",
    "TunnelOpts",
    "TunnelOption",
    "TunnelOptFunc",
    "with_disable_flow_control",
    "apply_tunnel_options",
    "normalize_options",
    # Context utilities
    "tunnel_channel_from_context",
    "tunnel_metadata_from_incoming_context",
    "tunnel_metadata_from_outgoing_context",
    "with_tunnel_channel",
    # Interceptors
    "InterceptedTunnelChannel",
    "LoggingInterceptor",
    "MetadataInterceptor",
    "intercept_tunnel_channel",
]
