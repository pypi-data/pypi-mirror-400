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

"""Tests for flow control mechanisms."""

import asyncio

import pytest

from grpctunnel.flow_control import (
    CHUNK_MAX,
    INITIAL_WINDOW_SIZE,
    FlowControlReceiver,
    FlowControlSender,
    NoFlowControlReceiver,
    NoFlowControlSender,
    new_receiver,
    new_receiver_without_flow_control,
    new_sender,
    new_sender_without_flow_control,
)


class TestFlowControlSender:
    """Tests for FlowControlSender."""

    @pytest.mark.asyncio
    async def test_send_small_message(self) -> None:
        """Test sending a message smaller than window size."""
        sent_chunks = []

        async def send_func(data: bytes, total_size: int, is_first: bool) -> None:
            sent_chunks.append((data, total_size, is_first))

        sender = new_sender(send_func)
        data = b"Hello, World!"
        await sender.send(data)

        assert len(sent_chunks) == 1
        assert sent_chunks[0][0] == data
        assert sent_chunks[0][1] == len(data)
        assert sent_chunks[0][2] is True

    @pytest.mark.asyncio
    async def test_send_large_message_chunks(self) -> None:
        """Test that large messages are split into chunks."""
        sent_chunks = []

        async def send_func(data: bytes, total_size: int, is_first: bool) -> None:
            sent_chunks.append((data, total_size, is_first))

        sender = new_sender(send_func)
        # Create a message larger than CHUNK_MAX
        data = b"X" * (CHUNK_MAX * 2 + 100)
        await sender.send(data)

        # Should be split into multiple chunks
        assert len(sent_chunks) >= 3
        # First chunk should be marked as first
        assert sent_chunks[0][2] is True
        # All chunks should report the same total size
        for chunk_data, total_size, _ in sent_chunks:
            assert total_size == len(data)
            assert len(chunk_data) <= CHUNK_MAX

    @pytest.mark.asyncio
    async def test_flow_control_window_limits(self) -> None:
        """Test that flow control limits sending when window is small."""
        sent_chunks = []
        window_updates = []

        async def send_func(data: bytes, total_size: int, is_first: bool) -> None:
            sent_chunks.append((data, total_size, is_first))
            # Small delay to simulate network
            await asyncio.sleep(0.001)

        sender = new_sender(send_func, initial_window_size=1000)

        # Send a large message that exceeds initial window
        data = b"X" * 5000

        # Start sending in background
        send_task = asyncio.create_task(sender.send(data))

        # Give it time to send initial chunks
        await asyncio.sleep(0.01)

        # Should have sent some chunks but not all
        initial_sent = len(sent_chunks)
        assert initial_sent > 0

        # Update window to allow more
        sender.update_window(5000)
        await send_task

        # Should have sent more chunks after window update
        assert len(sent_chunks) > initial_sent

    @pytest.mark.asyncio
    async def test_update_window(self) -> None:
        """Test that window updates allow more data to be sent."""
        sent_chunks = []

        async def send_func(data: bytes, total_size: int, is_first: bool) -> None:
            sent_chunks.append(len(data))

        sender = FlowControlSender(send_func, initial_window_size=100)

        # Send some data
        await sender.send(b"X" * 50)
        assert sum(sent_chunks) == 50

        # Update window
        sender.update_window(100)

        # Send more data
        await sender.send(b"Y" * 100)
        assert sum(sent_chunks) == 150


class TestFlowControlReceiver:
    """Tests for FlowControlReceiver."""

    @pytest.mark.asyncio
    async def test_accept_and_dequeue(self) -> None:
        """Test basic accept and dequeue operations."""
        window_updates = []

        def update_window(size: int) -> None:
            window_updates.append(size)

        def measure(item: bytes) -> int:
            return len(item)

        receiver = new_receiver(measure, update_window)

        # Accept some items
        await receiver.accept(b"Hello")
        await receiver.accept(b"World")

        # Dequeue items
        item1, ok1 = await receiver.dequeue()
        assert ok1 is True
        assert item1 == b"Hello"
        assert len(window_updates) == 1
        assert window_updates[0] == 5

        item2, ok2 = await receiver.dequeue()
        assert ok2 is True
        assert item2 == b"World"
        assert len(window_updates) == 2
        assert window_updates[1] == 5

    @pytest.mark.asyncio
    async def test_flow_control_window_exceeded(self) -> None:
        """Test that exceeding flow control window raises error."""

        def update_window(size: int) -> None:
            pass

        def measure(item: bytes) -> int:
            return len(item)

        receiver = FlowControlReceiver(measure, update_window, initial_window_size=10)

        # Try to accept item larger than window
        with pytest.raises(Exception):  # grpc.aio.AioRpcError
            await receiver.accept(b"X" * 100)

    @pytest.mark.asyncio
    async def test_close_receiver(self) -> None:
        """Test closing a receiver."""

        def update_window(size: int) -> None:
            pass

        def measure(item: bytes) -> int:
            return len(item)

        receiver = new_receiver(measure, update_window)

        # Close receiver
        receiver.close()

        # Dequeue should return False
        item, ok = await receiver.dequeue()
        assert ok is False
        assert item is None

    @pytest.mark.asyncio
    async def test_cancel_receiver(self) -> None:
        """Test cancelling a receiver clears items."""

        def update_window(size: int) -> None:
            pass

        def measure(item: bytes) -> int:
            return len(item)

        receiver = new_receiver(measure, update_window)

        # Accept items
        await receiver.accept(b"Hello")
        await receiver.accept(b"World")

        # Cancel receiver
        receiver.cancel()

        # Dequeue should return False immediately
        item, ok = await receiver.dequeue()
        assert ok is False
        assert item is None


class TestNoFlowControlSender:
    """Tests for NoFlowControlSender."""

    @pytest.mark.asyncio
    async def test_send_without_flow_control(self) -> None:
        """Test sending without flow control."""
        sent_chunks = []

        async def send_func(data: bytes, total_size: int, is_first: bool) -> None:
            sent_chunks.append((data, total_size, is_first))

        sender = new_sender_without_flow_control(send_func)
        data = b"Hello, World!"
        await sender.send(data)

        assert len(sent_chunks) == 1
        assert sent_chunks[0][0] == data
        assert sent_chunks[0][1] == len(data)
        assert sent_chunks[0][2] is True

    @pytest.mark.asyncio
    async def test_send_large_message_no_flow_control(self) -> None:
        """Test sending large message without flow control."""
        sent_chunks = []

        async def send_func(data: bytes, total_size: int, is_first: bool) -> None:
            sent_chunks.append((data, total_size, is_first))

        sender = NoFlowControlSender(send_func)
        data = b"X" * (CHUNK_MAX * 2 + 100)
        await sender.send(data)

        # Should still be chunked
        assert len(sent_chunks) >= 3
        assert sent_chunks[0][2] is True


class TestNoFlowControlReceiver:
    """Tests for NoFlowControlReceiver."""

    @pytest.mark.asyncio
    async def test_accept_and_dequeue_no_flow_control(self) -> None:
        """Test accept and dequeue without flow control."""
        receiver = new_receiver_without_flow_control()

        # Accept and dequeue should work
        accept_task = asyncio.create_task(receiver.accept(b"Hello"))
        await asyncio.sleep(0.01)  # Let accept start

        item, ok = await receiver.dequeue()
        assert ok is True
        assert item == b"Hello"

        await accept_task  # Ensure accept completed

    @pytest.mark.asyncio
    async def test_close_no_flow_control_receiver(self) -> None:
        """Test closing no-flow-control receiver."""
        receiver = NoFlowControlReceiver[bytes]()

        receiver.close()

        item, ok = await receiver.dequeue()
        assert ok is False
