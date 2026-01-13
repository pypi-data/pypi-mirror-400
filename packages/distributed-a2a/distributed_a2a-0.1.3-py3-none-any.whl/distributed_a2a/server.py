import asyncio
import time
from contextlib import asynccontextmanager

import boto3
from a2a.server.apps import A2ARESTFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentSkill, \
    AgentCapabilities, AgentCard, TransportProtocol
from fastapi import FastAPI

from .executors import RoutingAgentExecutor
from .registry import DynamoDbRegistryLookup

CAPABILITIES = AgentCapabilities(streaming=False, push_notifications=False)

HEART_BEAT_INTERVAL_SEC = 5
MAX_HEART_BEAT_MISSES = 3

AGENT_CARD_TABLE = "agent-cards"

def get_expire_at() -> int:
    return int(time.time() + MAX_HEART_BEAT_MISSES * HEART_BEAT_INTERVAL_SEC)

async def heart_beat(name: str, agent_card_table: str, agent_card: AgentCard):
    table = boto3.resource("dynamodb", region_name="eu-central-1").Table(agent_card_table)
    table.put_item(Item={"id": name, "card": agent_card.model_dump_json(), "expireAt": get_expire_at()})
    while True:
        await asyncio.sleep(HEART_BEAT_INTERVAL_SEC)
        table.update_item(
            Key={"id": name},
            UpdateExpression="SET expireAt = :expire_at",
            ExpressionAttributeValues={":expire_at": get_expire_at()}
        )


def load_app(name: str, description: str, skills: list[AgentSkill], api_key: str, system_prompt: str,
             host: str) -> FastAPI:

    routing_skill = AgentSkill(
        id='routing',
        name='Agent routing',
        description='Identifies the most suitable agent for the given task and returns the agent card',
        tags=['agent', 'routing']
    )

    agent_card = AgentCard(
        name=name,
        description=description,
        url=host,
        version='1.0.0',
        default_input_modes=['text', 'text/plain'],
        default_output_modes=['text', 'text/plain'],
        capabilities=CAPABILITIES,
        skills=skills + [routing_skill],
        preferred_transport=TransportProtocol.http_json
    )


    executor = RoutingAgentExecutor(api_key=api_key, system_prompt=system_prompt, routing_tool=DynamoDbRegistryLookup(agent_card_tabel=AGENT_CARD_TABLE).as_tool())

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        asyncio.create_task(heart_beat(name=name, agent_card_table=AGENT_CARD_TABLE, agent_card=agent_card))
        yield


    return A2ARESTFastAPIApplication(
        agent_card=agent_card,
        http_handler=DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore()
        )
    ).build(title=name, lifespan=lifespan)
