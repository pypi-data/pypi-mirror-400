# Development Notes - grpctunnel-py

## Project Management with uv

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management and project tooling. uv is a fast, reliable Python package manager written in Rust.

### Initial Setup

The project was initialized with uv and configured to use Python 3.11+:

```bash
# Initialize project
uv init grpctunnel-py
cd grpctunnel-py

# Set Python version
uv python pin 3.11

# Create source directory structure
mkdir -p src/grpctunnel
```

### Installing Dependencies

```bash
# Add production dependencies
uv add grpcio grpcio-tools protobuf

# Add development dependencies
uv add --dev pytest pytest-asyncio mypy black ruff

# Install the project in development mode
uv sync
```

### Common Development Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=grpctunnel

# Type checking
uv run mypy src/grpctunnel

# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Generate protobuf code
uv run python -m grpc_tools.protoc \
  -I. \
  --python_out=src/grpctunnel/proto/v1 \
  --grpc_python_out=src/grpctunnel/proto/v1 \
  --pyi_out=src/grpctunnel/proto/v1 \
  proto/grpctunnel/v1/tunnel.proto

# Run a specific test
uv run pytest tests/test_forward_tunnel.py -v

# Run integration tests (requires Go reference implementation)
uv run pytest tests/integration/ -v
```

### Project Structure

```
grpctunnel-py/
├── pyproject.toml          # Project metadata, dependencies, tool configs
├── uv.lock                 # Locked dependencies (committed to git)
├── .python-version         # Python version pinned by uv
├── PORTING_PLAN.md        # Detailed porting plan
├── CLAUDE.md              # This file - development notes
├── README.md              # User-facing documentation
├── src/
│   └── grpctunnel/        # Main package
│       ├── __init__.py
│       ├── py.typed       # PEP 561 marker for type hints
│       └── proto/         # Generated protobuf code
├── tests/                 # Test suite
│   ├── test_*.py          # Unit tests
│   └── integration/       # Integration tests
└── reference/
    └── grpctunnel/        # Original Go implementation (read-only)
```

### Why uv?

1. **Fast**: Written in Rust, significantly faster than pip/poetry
2. **Reliable**: Deterministic dependency resolution with lock file
3. **Simple**: Single tool for venv management, dependency resolution, and running scripts
4. **Modern**: First-class support for pyproject.toml and PEP standards
5. **Compatible**: Works with existing pip/setuptools projects

### uv vs pip/virtualenv

Traditional workflow:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

With uv:
```bash
uv sync              # Creates venv, installs all deps
uv run pytest        # Runs in the project's venv automatically
```

## Design Decisions

### Async-First Design

The Python port uses `asyncio` and `grpc.aio` for all I/O operations:

**Rationale**:
- gRPC async API is the recommended approach for new Python gRPC code
- Better resource utilization with async/await compared to threads
- More idiomatic Python for concurrent operations
- Easier to reason about with explicit async/await syntax

**Implications**:
- All public APIs are `async def`
- Users must use `asyncio.run()` or `await` to use the library
- Internal synchronization uses `asyncio.Lock` instead of `threading.Lock`

### Type Hints

All public APIs and most internal code includes comprehensive type hints:

**Benefits**:
- Catches bugs at development time with mypy
- Better IDE autocomplete and navigation
- Self-documenting code
- PEP 561 compliance with py.typed marker

**Convention**:
```python
from typing import Optional, List, Dict, Protocol, Generic, TypeVar

T = TypeVar('T')

class Sender(Protocol):
    async def send(self, data: bytes) -> None: ...
    def update_window(self, delta: int) -> None: ...

class Receiver(Generic[T], Protocol):
    async def accept(self, item: T) -> None: ...
    async def dequeue(self) -> Optional[T]: ...
```

### Error Handling

The library uses gRPC status codes and exceptions consistently:

```python
from grpc import StatusCode
from grpc.aio import AioRpcError

# Raise gRPC errors
raise AioRpcError(
    code=StatusCode.UNAVAILABLE,
    details="no channels ready"
)
```

Custom exceptions are avoided in favor of standard gRPC exceptions for consistency.

### Stream State Management

Each stream maintains its own state using dataclasses:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StreamState:
    stream_id: int
    method: str
    is_client_stream: bool
    is_server_stream: bool
    half_closed: bool = False
    done: Optional[Exception] = None
```

### Protocol Compatibility

The Python implementation aims for 100% wire-format compatibility with the Go version:

- Uses same protobuf definitions (copied from reference)
- Implements both REVISION_ZERO and REVISION_ONE
- Same flow control parameters (window size, chunk size)
- Same metadata handling
- Same negotiation headers

Interoperability is verified through integration tests with the Go implementation.

## Development Workflow

### Adding a New Feature

1. Read the corresponding Go code in `reference/grpctunnel/`
2. Write tests first (TDD approach)
3. Implement the feature with type hints
4. Run mypy to check types
5. Run tests with pytest
6. Format with black, lint with ruff
7. Update documentation if needed

### Running Integration Tests

Integration tests require the Go reference implementation to be built:

```bash
# Build Go test servers/clients (one time)
cd reference/grpctunnel
go build ./internal/cmd/tunneltestsvr
go build ./internal/cmd/tunneltestclient

# Run Python integration tests
cd ../..
uv run pytest tests/integration/
```

### Debugging

```bash
# Run with verbose output
uv run pytest tests/ -v -s

# Run with debugger on failure
uv run pytest tests/ --pdb

# Run specific test with logging
uv run pytest tests/test_client.py::test_forward_tunnel -v --log-cli-level=DEBUG
```

## Python-Specific Challenges

### 1. Context Values

**Go**: Uses `context.Context` with arbitrary key-value pairs
```go
ctx = context.WithValue(ctx, myKey{}, myValue)
```

**Python**: Use contextvars module
```python
from contextvars import ContextVar

tunnel_metadata_var: ContextVar[grpc.aio.Metadata] = ContextVar('tunnel_metadata')

# Set value
tunnel_metadata_var.set(metadata)

# Get value
metadata = tunnel_metadata_var.get()
```

### 2. Goroutines vs Async Tasks

**Go**: Spawn goroutine with `go func()`
```go
go func() {
    // background work
}()
```

**Python**: Create async task
```python
task = asyncio.create_task(background_work())

# Don't forget to track and await tasks during cleanup!
```

### 3. Channels vs Queues

**Go**: Use channels for communication
```go
ch := make(chan Message, 10)
ch <- msg
msg := <-ch
```

**Python**: Use asyncio.Queue
```python
queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=10)
await queue.put(msg)
msg = await queue.get()
```

### 4. Select vs wait/gather

**Go**: Use select statement
```go
select {
case msg := <-ch:
    // handle message
case <-ctx.Done():
    // handle cancellation
}
```

**Python**: Use asyncio.wait with FIRST_COMPLETED
```python
done, pending = await asyncio.wait(
    [queue_task, cancel_task],
    return_when=asyncio.FIRST_COMPLETED
)
```

### 5. Mutexes vs Locks

**Go**: Use sync.Mutex or sync.RWMutex
```go
mu sync.Mutex
mu.Lock()
defer mu.Unlock()
```

**Python**: Use asyncio.Lock
```python
lock = asyncio.Lock()
async with lock:
    # critical section
```

### 6. Atomic Operations

**Go**: Use sync/atomic package
```go
var counter atomic.Int64
counter.Add(1)
val := counter.Load()
```

**Python**: Use threading.Lock or single-threaded async
```python
# In async code, no atomics needed (single-threaded)
counter = 0
counter += 1

# If needed, use asyncio.Lock as shown above
```

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock gRPC streams and channels
- Test error conditions
- Test protocol negotiation

### Integration Tests (Python-only)
- Full end-to-end within Python
- Python client -> Python server
- Multiple concurrent streams
- Flow control behavior
- Shutdown scenarios

### Interoperability Tests
- Python client -> Go server (forward)
- Go client -> Python server (forward)
- Python client -> Go server (reverse)
- Go client -> Python server (reverse)
- Both protocol revisions
- Large messages
- High concurrency

### Test Fixtures

Use pytest fixtures for common setup:

```python
import pytest
import grpc.aio

@pytest.fixture
async def server():
    server = grpc.aio.server()
    # setup
    await server.start()
    yield server
    await server.stop(grace=None)

@pytest.fixture
async def channel():
    channel = grpc.aio.insecure_channel('localhost:50051')
    yield channel
    await channel.close()
```

## Performance Considerations

### Message Chunking
- Large messages are split into 16KB chunks
- Prevents head-of-line blocking
- Allows fair scheduling of concurrent streams

### Flow Control
- Initial window: 65536 bytes (64KB)
- Window updates sent after processing data
- Prevents memory exhaustion from fast senders

### Buffering
- Per-stream unbounded queues (with flow control)
- Channel-level send/receive loops
- asyncio.Queue for efficient async operations

## Future Enhancements

### Potential Improvements
1. Configurable window sizes
2. Compression support
3. Custom codec support
4. Metrics/monitoring integration
5. Connection pooling for reverse tunnels
6. Automatic retry/reconnection
7. Load balancing strategies beyond round-robin

### Known Limitations
1. Python's GIL may limit performance vs Go
2. Memory usage higher due to Python overhead
3. Async debugging can be challenging
4. No bidirectional streaming without asyncio

## Contributing Guidelines

When contributing to this project:

1. Follow PEP 8 style (enforced by black/ruff)
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Run full test suite before submitting
6. Maintain compatibility with Go implementation

## Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [grpcio documentation](https://grpc.io/docs/languages/python/)
- [asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Original grpctunnel (Go)](https://github.com/jhump/grpctunnel)
- [Protocol Buffers](https://protobuf.dev/getting-started/pythontutorial/)

## License

This project is licensed under Apache License 2.0, same as the original Go implementation.

**Original Author**: Joshua Humphries (jhump)
**Original Repository**: https://github.com/jhump/grpctunnel

This Python port maintains the same license and includes proper attribution to the original work.
