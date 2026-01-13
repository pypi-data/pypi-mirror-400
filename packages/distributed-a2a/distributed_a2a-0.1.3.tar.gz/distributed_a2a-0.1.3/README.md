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

## Components

### StatusAgent

A base agent class that provides status tracking and structured responses:

```python
from distributed_a2a import StatusAgent, StringResponse

agent = StatusAgent[StringResponse](
    system_prompt="Your system prompt",
    name="AgentName",
    api_key="your-api-key",
    is_routing=False,
    tools=[]
)

response = await agent("User message", context_id="context-123")
```

### RoutingAgentExecutor

An executor that can handle requests directly or route them to specialized agents:

```python
from distributed_a2a import RoutingAgentExecutor

executor = RoutingAgentExecutor(
    api_key="your-api-key",
    system_prompt="Your system prompt",
    routing_tool=routing_tool
)
```

### DynamoDB Registry

Dynamic agent registry with automatic heartbeat and expiration:

```python
from distributed_a2a import DynamoDbRegistryLookup

registry = DynamoDbRegistryLookup(agent_card_tabel="agent-cards")
tool = registry.as_tool()
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
