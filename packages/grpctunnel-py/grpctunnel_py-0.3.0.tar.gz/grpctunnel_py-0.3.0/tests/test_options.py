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

"""Tests for tunnel options."""

from grpctunnel.options import (
    TunnelOptions,
    TunnelOpts,
    TunnelOption,
    TunnelOptFunc,
    with_disable_flow_control,
    WithDisableFlowControl,
    apply_tunnel_options,
    normalize_options
)
from grpctunnel.proto.v1 import REVISION_ONE, REVISION_ZERO


class TestTunnelOptions:
    """Tests for TunnelOptions."""

    def test_default_options(self) -> None:
        """Test default TunnelOptions configuration."""
        opts = TunnelOptions()
        assert opts.disable_flow_control is False
        revisions = opts.supported_revisions()
        assert REVISION_ZERO in revisions
        assert REVISION_ONE in revisions
        assert len(revisions) == 2

    def test_disable_flow_control(self) -> None:
        """Test TunnelOptions with flow control disabled."""
        opts = TunnelOptions(disable_flow_control=True)
        assert opts.disable_flow_control is True
        revisions = opts.supported_revisions()
        assert revisions == [REVISION_ZERO]
        assert REVISION_ONE not in revisions

    def test_with_disable_flow_control_factory(self) -> None:
        """Test with_disable_flow_control factory function (legacy)."""
        # Test that the old function still returns TunnelOptions
        opts = WithDisableFlowControl()
        assert isinstance(opts, TunnelOptions)
        assert opts.disable_flow_control is True
        revisions = opts.supported_revisions()
        assert revisions == [REVISION_ZERO]

    def test_supported_revisions_order(self) -> None:
        """Test that supported revisions are in correct order."""
        opts = TunnelOptions()
        revisions = opts.supported_revisions()
        # REVISION_ZERO should come before REVISION_ONE
        assert revisions[0] == REVISION_ZERO
        assert revisions[1] == REVISION_ONE


class TestTunnelOption:
    """Tests for the new TunnelOption protocol interface."""

    def test_tunnel_opt_func(self) -> None:
        """Test TunnelOptFunc implementation."""
        # Create a custom option using TunnelOptFunc
        custom_called = False

        def custom_apply(opts: TunnelOpts):
            nonlocal custom_called
            custom_called = True
            opts.disable_flow_control = True

        option = TunnelOptFunc(custom_apply)
        opts = TunnelOpts()

        # Apply the option
        option.apply(opts)

        assert custom_called
        assert opts.disable_flow_control is True

    def test_with_disable_flow_control_new(self) -> None:
        """Test the new with_disable_flow_control function."""
        option = with_disable_flow_control()

        # Verify it implements TunnelOption protocol
        assert hasattr(option, 'apply')

        # Apply the option
        opts = TunnelOpts()
        option.apply(opts)
        assert opts.disable_flow_control is True
        assert opts.supported_revisions() == [REVISION_ZERO]

    def test_apply_tunnel_options(self) -> None:
        """Test applying multiple options."""
        # Create multiple options
        option1 = with_disable_flow_control()

        # Create a custom option
        def custom_apply(opts: TunnelOpts):
            # This would normally set a different field
            # For testing, we'll just verify it's called
            pass

        option2 = TunnelOptFunc(custom_apply)

        # Apply multiple options
        opts = apply_tunnel_options(option1, option2)
        assert opts.disable_flow_control is True

    def test_apply_tunnel_options_empty(self) -> None:
        """Test applying no options."""
        opts = apply_tunnel_options()
        assert opts.disable_flow_control is False
        assert REVISION_ONE in opts.supported_revisions()

    def test_normalize_options_none(self) -> None:
        """Test normalizing None options."""
        opts = normalize_options(None)
        assert isinstance(opts, TunnelOpts)
        assert opts.disable_flow_control is False

    def test_normalize_options_legacy(self) -> None:
        """Test normalizing legacy TunnelOptions."""
        legacy = TunnelOptions(disable_flow_control=True)
        opts = normalize_options(legacy)
        assert isinstance(opts, TunnelOpts)
        assert opts.disable_flow_control is True

    def test_normalize_options_single(self) -> None:
        """Test normalizing a single TunnelOption."""
        option = with_disable_flow_control()
        opts = normalize_options(option)
        assert isinstance(opts, TunnelOpts)
        assert opts.disable_flow_control is True

    def test_normalize_options_list(self) -> None:
        """Test normalizing a list of TunnelOptions."""
        options = [with_disable_flow_control()]
        opts = normalize_options(options)
        assert isinstance(opts, TunnelOpts)
        assert opts.disable_flow_control is True

    def test_protocol_compatibility(self) -> None:
        """Test that TunnelOptFunc satisfies the TunnelOption protocol."""
        option = with_disable_flow_control()

        # Check it has the required method
        assert hasattr(option, 'apply')
        assert callable(option.apply)

        # Verify it works as a TunnelOption
        def process_option(opt: TunnelOption) -> TunnelOpts:
            """Function that accepts TunnelOption protocol."""
            opts = TunnelOpts()
            opt.apply(opts)
            return opts

        result = process_option(option)
        assert result.disable_flow_control is True
