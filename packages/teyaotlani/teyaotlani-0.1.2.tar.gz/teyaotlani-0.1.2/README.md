# Teyaotlani

**Modern Spartan protocol server and client implementation using asyncio**

[![Documentation](https://readthedocs.org/projects/teyaotlani/badge/?version=latest)](https://teyaotlani.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Teyaotlani (from Nahuatl: "warrior") is a Python library for building Spartan protocol servers and clients. It provides an async-first design with a clean, intuitive API.

## Features

- **Async-first design** - Built on asyncio for high-performance concurrent connections
- **Full protocol support** - Complete Spartan client and server implementation
- **CLI included** - Command-line tools for fetching, uploading, and serving content
- **Configurable server** - Rate limiting, access control, and upload handling
- **Type-safe** - Full type annotations for modern Python development

## Installation

```bash
# Using uv (recommended)
uv add teyaotlani

# Using pip
pip install teyaotlani
```

## Quick Start

### Client

```python
import asyncio
from teyaotlani import get

async def main():
    response = await get("spartan://example.com/")
    print(response.body)

asyncio.run(main())
```

### Server

```python
import asyncio
from teyaotlani import ServerConfig, run_server

async def main():
    config = ServerConfig(
        host="localhost",
        port=3000,
        document_root="./capsule",
    )
    await run_server(config)

asyncio.run(main())
```

### CLI

```bash
# Fetch a page
teyaotlani get spartan://example.com/

# Serve files
teyaotlani serve ./capsule --port 3000

# Upload content
teyaotlani upload spartan://localhost:3000/file.txt -c "Hello!"
```

## Documentation

Full documentation is available at [teyaotlani.readthedocs.io](https://teyaotlani.readthedocs.io/).

- [Installation](https://teyaotlani.readthedocs.io/tutorials/installation/)
- [Quick Start](https://teyaotlani.readthedocs.io/tutorials/quick-start/)
- [API Reference](https://teyaotlani.readthedocs.io/reference/api/)

## What is Spartan?

Spartan is a simple, text-focused internet protocol similar to Gemini but without TLS complexity. It's designed for:

- Lightweight content serving
- Native file uploads
- Easy implementation
- Internal networks and learning

Learn more in the [Spartan Protocol explanation](https://teyaotlani.readthedocs.io/explanation/spartan-protocol/).

## License

MIT License - see [LICENSE](LICENSE) for details.
