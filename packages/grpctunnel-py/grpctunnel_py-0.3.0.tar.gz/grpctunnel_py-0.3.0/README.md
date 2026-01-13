# grpctunnel-py

A Python port of [grpctunnel](https://github.com/jhump/grpctunnel) - a library for carrying gRPC over gRPC.

## About

This library enables tunneling gRPC connections through other gRPC connections. This provides two primary use cases:

1. **Forward Tunnels**: Pin multiple RPC calls to a single server backend, providing session affinity even when
   connecting through load balancers.

2. **Reverse Tunnels**: Allow servers to send RPC requests back to connected clients, enabling rich "server push"
   capabilities and allowing servers behind NAT/firewalls to be accessed.

## Attribution

This is a Python port of the original Go implementation created by **Joshua Humphries**.

- **Original Author**: Joshua Humphries ([@jhump](https://github.com/jhump))
- **Original Repository**: https://github.com/jhump/grpctunnel
- **License**: Apache License 2.0

This Python port maintains compatibility with the original Go implementation, allowing Python and Go clients/servers to
interoperate seamlessly.

## Installation

```bash
pip install grpctunnel-py
```

Or with uv:

```bash
uv add grpctunnel-py
```

## Requirements

- Python 3.11+
- grpcio
- protobuf

## License

Copyright 2025 Daniel Valdivia

Ported from the original Go implementation by Joshua Humphries.
Original: https://github.com/jhump/grpctunnel

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Links

- [Original Go implementation](https://github.com/jhump/grpctunnel)
- [gRPC Python](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://protobuf.dev/)
- [uv - Python package manager](https://github.com/astral-sh/uv)

## Acknowledgments

Special thanks to **Joshua Humphries** ([@jhump](https://github.com/jhump)) for creating the original grpctunnel library
and for the excellent design that made this port possible.
