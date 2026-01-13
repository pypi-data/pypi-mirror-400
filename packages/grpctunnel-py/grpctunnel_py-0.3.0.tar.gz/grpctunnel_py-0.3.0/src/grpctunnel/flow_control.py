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

"""Flow control mechanisms for the gRPC tunnel.

This module implements flow control for tunneled streams to prevent deadlock
and memory exhaustion. It provides both flow-controlled and non-flow-controlled
variants to support different protocol revisions.
"""

import asyncio
import sys
from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Coroutine, Generic, TypeVar

import grpc

# Constants from the Go implementation
INITIAL_WINDOW_SIZE = 65536  # 64KB initial window
CHUNK_MAX = 16384  # 16KB max chunk size

# Error for flow control violations
_ERR_FLOW_CONTROL_WINDOW_EXCEEDED = grpc.StatusCode.RESOURCE_EXHAUSTED


T = TypeVar("T")


class Sender(ABC):
    """Abstract base class for sending messages with optional flow control."""

    @abstractmethod
    async def send(self, data: bytes) -> None:
        """Send data, potentially splitting it into chunks.

        Args:
            data: The message data to send

        Raises:
            grpc.RpcError: If the data is too large or context is cancelled
        """
        pass

    @abstractmethod
    def update_window(self, add: int) -> None:
        """Update the flow control window.

        Args:
            add: Number of bytes to add to the window
        """
        pass


class Receiver(ABC, Generic[T]):
    """Abstract base class for receiving messages with optional flow control."""

    @abstractmethod
    async def accept(self, item: T) -> None:
        """Accept an item into the receiver queue.

        Args:
            item: The item to accept

        Raises:
            grpc.RpcError: If flow control window is exceeded
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the receiver normally (graceful shutdown)."""
        pass

    @abstractmethod
    def cancel(self) -> None:
        """Cancel the receiver abruptly (clear all pending items)."""
        pass

    @abstractmethod
    async def dequeue(self) -> tuple[T | None, bool]:
        """Dequeue the next item from the receiver.

        Returns:
            A tuple of (item, ok) where ok is False if the receiver is closed/cancelled
            and item is None when ok is False
        """
        pass


# Type for the send function callback
SendFunc = Callable[[bytes, int, bool], Coroutine[None, None, None]]


class FlowControlSender(Sender):
    """Sender with flow control window management."""

    def __init__(
        self,
        send_func: SendFunc,
        initial_window_size: int = INITIAL_WINDOW_SIZE,
    ):
        """Initialize a flow control sender.

        Args:
            send_func: Callback function(data, total_size, is_first) to send chunks
            initial_window_size: Initial flow control window size in bytes
        """
        self._send_func = send_func
        self._current_window = initial_window_size
        self._window_update_event = asyncio.Event()
        self._send_lock = asyncio.Lock()
        self._window_lock = asyncio.Lock()
        self._closed = False

    def update_window(self, add: int) -> None:
        """Update the flow control window by adding bytes."""
        if add == 0:
            return

        # We need synchronous access to the window
        # In Python with GIL, simple int operations are atomic,
        # but we use a lock for clarity and future safety
        prev_window = self._current_window
        self._current_window += add

        # If window was exhausted (0), signal waiting senders
        if prev_window == 0:
            self._window_update_event.set()

    async def send(self, data: bytes) -> None:
        """Send data with flow control, splitting into chunks as needed."""
        async with self._send_lock:
            if self._closed:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.CANCELLED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="sender closed",
                )

            data_len = len(data)
            if data_len > sys.maxsize:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.RESOURCE_EXHAUSTED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"serialized message is too large: {data_len} bytes",
                )

            total_size = data_len
            first = True
            offset = 0

            while offset < data_len:
                # Wait for available window
                while True:
                    async with self._window_lock:
                        window_sz = self._current_window
                        if window_sz > 0:
                            break

                    # Window exhausted, wait for update
                    self._window_update_event.clear()
                    await self._window_update_event.wait()

                # Calculate chunk size
                async with self._window_lock:
                    window_sz = self._current_window
                    remaining = data_len - offset
                    chunk_sz = min(window_sz, remaining, CHUNK_MAX)
                    self._current_window -= chunk_sz

                # Send the chunk
                chunk = data[offset : offset + chunk_sz]
                await self._send_func(chunk, total_size, first)

                first = False
                offset += chunk_sz

    def close(self) -> None:
        """Close the sender."""
        self._closed = True
        self._window_update_event.set()


class FlowControlReceiver(Receiver[T], Generic[T]):
    """Receiver with flow control window management and unbounded queue."""

    def __init__(
        self,
        measure: Callable[[T], int],
        update_window: Callable[[int], None],
        initial_window_size: int = INITIAL_WINDOW_SIZE,
    ):
        """Initialize a flow control receiver.

        Args:
            measure: Function to measure the size of an item in bytes
            update_window: Callback to send window updates
            initial_window_size: Initial flow control window size in bytes
        """
        self._measure = measure
        self._update_window = update_window
        self._items: deque[T] = deque()
        self._current_window = initial_window_size
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)
        self._closed = False
        self._cancelled = False

    async def accept(self, item: T) -> None:
        """Accept an item, checking flow control window."""
        size = self._measure(item)

        async with self._lock:
            if self._closed or self._cancelled:
                return

            if size > self._current_window:
                raise grpc.aio.AioRpcError(
                    code=_ERR_FLOW_CONTROL_WINDOW_EXCEEDED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="flow control window exceeded",
                )

            self._current_window -= size
            was_empty = len(self._items) == 0
            self._items.append(item)

            if was_empty:
                self._not_empty.notify()

    def close(self) -> None:
        """Close the receiver gracefully."""
        # We can't use async lock in a sync method, but we can use a
        # different approach: set a flag and notify waiters
        # This is safe because we're just setting a boolean
        if not self._closed:
            self._closed = True
            # Schedule notification on the event loop
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(self._notify_close)
            except RuntimeError:
                # No running loop, can't notify
                pass

    def _notify_close(self) -> None:
        """Notify waiting dequeuers of close (must be called from event loop)."""
        # This will be called from the event loop
        async def _do_notify() -> None:
            async with self._not_empty:
                self._not_empty.notify_all()

        asyncio.create_task(_do_notify())

    def cancel(self) -> None:
        """Cancel the receiver abruptly, clearing all items."""
        if not self._cancelled:
            self._cancelled = True
            # Clear items to free memory
            self._items.clear()
            # Notify waiters
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(self._notify_cancel)
            except RuntimeError:
                pass

    def _notify_cancel(self) -> None:
        """Notify waiting dequeuers of cancel (must be called from event loop)."""
        async def _do_notify() -> None:
            async with self._not_empty:
                self._not_empty.notify_all()

        asyncio.create_task(_do_notify())

    async def dequeue(self) -> tuple[T | None, bool]:
        """Dequeue the next item, sending window updates."""
        async with self._not_empty:
            while True:
                if self._cancelled:
                    return None, False

                if len(self._items) > 0:
                    item = self._items.popleft()
                    size = self._measure(item)
                    self._current_window += size
                    # Send window update
                    # TODO: Support minimum update size to batch updates
                    self._update_window(size)
                    return item, True

                if self._closed:
                    return None, False

                await self._not_empty.wait()


class NoFlowControlSender(Sender):
    """Sender without flow control (for REVISION_ZERO compatibility)."""

    def __init__(self, send_func: SendFunc):
        """Initialize a no-flow-control sender.

        Args:
            send_func: Callback function(data, total_size, is_first) to send chunks
        """
        self._send_func = send_func
        self._send_lock = asyncio.Lock()
        self._closed = False

    def update_window(self, add: int) -> None:
        """No-op for no flow control sender."""
        pass  # Should never actually be called

    async def send(self, data: bytes) -> None:
        """Send data without flow control, splitting into chunks."""
        async with self._send_lock:
            if self._closed:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.CANCELLED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details="sender closed",
                )

            data_len = len(data)
            if data_len > sys.maxsize:
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.RESOURCE_EXHAUSTED,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"serialized message is too large: {data_len} bytes",
                )

            total_size = data_len
            first = True
            offset = 0

            while offset < data_len:
                remaining = data_len - offset
                chunk_sz = min(CHUNK_MAX, remaining)
                chunk = data[offset : offset + chunk_sz]
                await self._send_func(chunk, total_size, first)
                first = False
                offset += chunk_sz

    def close(self) -> None:
        """Close the sender."""
        self._closed = True


class NoFlowControlReceiver(Receiver[T], Generic[T]):
    """Receiver without flow control (for REVISION_ZERO compatibility)."""

    def __init__(self) -> None:
        """Initialize a no-flow-control receiver."""
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=1)
        self._closed = False
        self._accept_lock = asyncio.Lock()

    async def accept(self, item: T) -> None:
        """Accept an item into the queue."""
        async with self._accept_lock:
            if self._closed:
                return
            try:
                await self._queue.put(item)
            except asyncio.CancelledError:
                # Queue was closed
                pass

    def close(self) -> None:
        """Close the receiver."""
        if not self._closed:
            self._closed = True
            # Put a sentinel to wake up any waiting dequeue
            try:
                self._queue.put_nowait(None)  # type: ignore
            except asyncio.QueueFull:
                pass

    def cancel(self) -> None:
        """Cancel is the same as close for no flow control."""
        self.close()

    async def dequeue(self) -> tuple[T | None, bool]:
        """Dequeue the next item."""
        try:
            item = await self._queue.get()
            if item is None:  # Sentinel value for closed
                return None, False
            return item, True
        except asyncio.CancelledError:
            return None, False


# Factory functions matching the Go implementation


def new_sender(
    send_func: SendFunc, initial_window_size: int = INITIAL_WINDOW_SIZE
) -> Sender:
    """Create a flow control sender.

    Args:
        send_func: Callback to send message chunks
        initial_window_size: Initial window size in bytes

    Returns:
        A Sender with flow control
    """
    return FlowControlSender(send_func, initial_window_size)


def new_sender_without_flow_control(send_func: SendFunc) -> Sender:
    """Create a sender without flow control.

    Args:
        send_func: Callback to send message chunks

    Returns:
        A Sender without flow control
    """
    return NoFlowControlSender(send_func)


def new_receiver(
    measure: Callable[[T], int],
    update_window: Callable[[int], None],
    initial_window_size: int = INITIAL_WINDOW_SIZE,
) -> Receiver[T]:
    """Create a flow control receiver.

    Args:
        measure: Function to measure item size in bytes
        update_window: Callback to send window updates
        initial_window_size: Initial window size in bytes

    Returns:
        A Receiver with flow control
    """
    return FlowControlReceiver(measure, update_window, initial_window_size)


def new_receiver_without_flow_control() -> Receiver[T]:
    """Create a receiver without flow control.

    Returns:
        A Receiver without flow control
    """
    return NoFlowControlReceiver()
