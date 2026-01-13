# A2A Agent Library

A Python library for building A2A (Agent-to-Agent) agents with routing capabilities, DynamoDB-backed registry, and LangChain integration.

## Features

- **StatusAgent**: Base agent implementation with status tracking and structured responses
- **RoutingAgentExecutor**: Agent executor with intelligent routing capabilities
- **DynamoDB Registry**: Dynamic agent card registry with heartbeat mechanism
- **Server Utilities**: FastAPI application builder with A2A protocol support
- **LangChain Integration**: Built on LangChain for flexible model integration

## Installation

```bash
pip install distributed-a2a
```

## Quick Start

1. Start a server with your agent application:
```python
from distributed_a2a import load_app
from a2a.types import AgentSkill

# Define your agent's skills
skills = [
    AgentSkill(
        id='example_skill',
        name='Example Skill',
        description='An example skill',
        tags=['example']
    )
]

# Create your agent application
app = load_app(
    name="MyAgent",
    description="My specialized agent",
    skills=skills,
    api_key="your-api-key",
    system_prompt="You are a helpful assistant...",
    host="http://localhost:8000"
)
```

2. Send a request with the client
```python
from uuid import uuid4

from distributed_a2a import RoutingA2AClient

if __name__ == "__main__":
    import asyncio

    request = "Tell me the weather in Bonn"
    client = RoutingA2AClient("http://localhost:8000")
    response: str = asyncio.run(client.send_message(request, str(uuid4())))
    print(response)
```

## Requirements

- Python 3.10+
- langchain
- langchain-core
- langchain-openai
- langgraph
- pydantic
- boto3
- a2a

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
