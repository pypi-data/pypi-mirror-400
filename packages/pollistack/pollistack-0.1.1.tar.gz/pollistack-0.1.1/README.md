# pollistack

Python SDK for the PolliStack Agent Engine.

## Installation

```bash
pip install pollistack
```

## Quick Start

```python
import asyncio
from pollistack.client import PolliClient

async def main():
    client = PolliClient(
    base_url='https://api.meridian-labs.ai',
    api_key='your-api-key'
)
    
    response = await client.chat(
        prompt="Hello, my name is Alice.",
        user_id="alice-123",
        app_id="my-app"
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### `PolliClient`

- `chat(prompt, user_id, app_id=None, model="qwen-coder")`: Send a prompt.
- `sync(query, user_id, content=None, app_id=None)`: Sync memory.
- `retrieve(query, user_id, app_id=None)`: Get relevant context.
- `remember(prompt, response, user_id, app_id=None)`: Extract memory.
- `get_graph(user_id, limit=50, app_id=None)`: Fetch graph.

## License

MIT
