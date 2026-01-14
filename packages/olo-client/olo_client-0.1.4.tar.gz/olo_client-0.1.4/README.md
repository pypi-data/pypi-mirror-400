# OLO Python SDK

Python SDK for controlling robots via ROS (Robot Operating System) through WebSocket connections.

## Installation

```bash
pip install olo-client
```

### Optional Dependencies

For WebRTC video streaming support:

```bash
pip install olo-client[video]
```

For all optional features:

```bash
pip install olo-client[full]
```

## Quick Start

```python
import asyncio
from oloclient import OLOClient

async def main():
    # Connect to ROS bridge
    async with OLOClient(ros_url='ws://localhost:9090') as client:
        # List available topics
        topics = await client.core.list_topics()
        print(f"Found {len(topics)} topics")

asyncio.run(main())
```

## Documentation

For full API documentation, see the [OLO Documentation](https://app.olo-robotics.com/documentation/).
