# Codacle Graph SDK

Python SDK for the Codacle Graph Service API. Provides sync/async clients with statically typed models for Neo4j graph operations.

## Installation

```bash
pip install codacle-graph-sdk
```

## Quick Start

### Sync Client

```python
from codacle_graph_sdk import CodacleGraphClient

with CodacleGraphClient(
    url="https://api.codacle.com",
    api_key="your-api-key",
    alias="production-db",
) as client:
    result = client.cypher_query("MATCH (c:Class) RETURN c LIMIT 10")
    for node in result.get_nodes():
        print(node.name)
```

### Async Client

```python
import asyncio
from codacle_graph_sdk import AsyncCodacleGraphClient

async def main():
    async with AsyncCodacleGraphClient(
        url="https://api.codacle.com",
        api_key="your-api-key",
    ) as client:
        result = await client.cypher_query("MATCH (m:Module) RETURN m")
        print(result.get_nodes())

asyncio.run(main())
```

## Features

- Sync and async clients
- Typed node models (Client, Application, Module, Class, Subroutine, etc.)
- Typed relationship models
- Convenience methods for graph traversal
- Exception hierarchy mirroring API errors

## License

MIT
