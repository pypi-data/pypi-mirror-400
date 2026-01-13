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

"""Configuration options for tunnel clients and servers.

This module provides options for configuring the behavior of tunnel clients
and servers, including protocol revision selection and flow control settings.
"""

from dataclasses import dataclass, field
from typing import Protocol, Callable, List, Optional

from grpctunnel.proto.v1 import REVISION_ONE, REVISION_ZERO, ProtocolRevision


class TunnelOption(Protocol):
    """Protocol for tunnel configuration options.

    This protocol defines the interface for tunnel options, matching the
    Go implementation's TunnelOption interface.
    """

    def apply(self, opts: "TunnelOpts") -> None:
        """Apply this option to the given tunnel options."""
        ...


@dataclass
class TunnelOpts:
    """Internal representation of tunnel configuration.

    This class holds the actual configuration state, similar to the
    Go implementation's tunnelOpts struct.
    """

    disable_flow_control: bool = False

    def supported_revisions(self) -> List[int]:
        """Get the list of protocol revisions supported by these options.

        Returns:
            List of ProtocolRevision values in order of preference.
            If flow control is disabled, only REVISION_ZERO is returned.
            Otherwise, both REVISION_ZERO and REVISION_ONE are returned.
        """
        if self.disable_flow_control:
            return [REVISION_ZERO]
        return [REVISION_ZERO, REVISION_ONE]


# Keep the old name for backward compatibility
@dataclass
class TunnelOptions:
    """Options for configuring tunnel behavior.

    Attributes:
        disable_flow_control: If True, disables flow control even when peer supports it.
            This is intended for testing compatibility with older versions and should NOT
            be used in production code. Default: False
    """

    disable_flow_control: bool = False

    def supported_revisions(self) -> list[int]:
        """Get the list of protocol revisions supported by these options.

        Returns:
            List of ProtocolRevision values in order of preference.
            If flow control is disabled, only REVISION_ZERO is returned.
            Otherwise, both REVISION_ZERO and REVISION_ONE are returned.
        """
        if self.disable_flow_control:
            return [REVISION_ZERO]
        return [REVISION_ZERO, REVISION_ONE]


class TunnelOptFunc:
    """Function-based implementation of TunnelOption.

    This class wraps a function to implement the TunnelOption protocol,
    similar to the Go implementation's tunnelOptFunc type.
    """

    def __init__(self, func: Callable[[TunnelOpts], None]):
        """Initialize with a function that modifies TunnelOpts."""
        self._func = func

    def apply(self, opts: TunnelOpts) -> None:
        """Apply this option by calling the wrapped function."""
        self._func(opts)


def with_disable_flow_control() -> TunnelOption:
    """Create a TunnelOption that disables flow control.

    NOTE: This should NOT be used in application code. This is intended
    for test code, to verify that tunnels work without flow control,
    to ensure correct interop with older versions of this package.

    Eventually, older versions that do not use flow control will not
    be supported and this option may be removed.

    Returns:
        TunnelOption that disables flow control when applied
    """
    def apply_func(opts: TunnelOpts):
        opts.disable_flow_control = True

    return TunnelOptFunc(apply_func)


# Legacy function for backward compatibility
def WithDisableFlowControl() -> TunnelOptions:
    """Legacy function for backward compatibility.

    Use with_disable_flow_control() instead.

    Returns:
        TunnelOptions with disable_flow_control=True
    """
    return TunnelOptions(disable_flow_control=True)


def apply_tunnel_options(*options: TunnelOption) -> TunnelOpts:
    """Apply a list of TunnelOptions and return the configured TunnelOpts.

    This function applies all provided options to a new TunnelOpts instance,
    similar to how the Go implementation processes options.

    Args:
        *options: Variable number of TunnelOption instances to apply

    Returns:
        TunnelOpts with all options applied
    """
    opts = TunnelOpts()
    for option in options:
        if option is not None:
            option.apply(opts)
    return opts


def normalize_options(options: Optional[TunnelOptions | TunnelOption | List[TunnelOption]]) -> TunnelOpts:
    """Normalize various option formats to TunnelOpts.

    This helper function handles backward compatibility by accepting the old
    TunnelOptions dataclass, a single TunnelOption, or a list of TunnelOptions.

    Args:
        options: Options in various formats

    Returns:
        Normalized TunnelOpts instance
    """
    if options is None:
        return TunnelOpts()
    elif isinstance(options, TunnelOptions):
        # Legacy dataclass format
        return TunnelOpts(disable_flow_control=options.disable_flow_control)
    elif isinstance(options, list):
        # List of new-style options
        return apply_tunnel_options(*options)
    else:
        # Single new-style option
        return apply_tunnel_options(options)
