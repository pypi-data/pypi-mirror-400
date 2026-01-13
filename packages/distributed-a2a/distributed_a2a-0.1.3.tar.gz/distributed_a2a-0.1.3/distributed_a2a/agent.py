from typing import Literal

from a2a.types import TaskState
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from .model import get_model


class AgentResponse(BaseModel):
    status: Literal[TaskState.rejected, TaskState.completed, TaskState.rejected, TaskState.failed] = Field(
        description=(
            f'You should select status as {TaskState.rejected} for requests that fall outside your area of expertise.'
            f'You should select status as {TaskState.completed} if the request is fully addressed and no further input is needed. '
            f'You should select status as {TaskState.input_required} if you need more information from the user or are asking a clarifying question. '
            f'You should select status as {TaskState.failed} if an error occurred or the request cannot be fulfilled.'
        )
    )

class RoutingResponse(AgentResponse):
    agent_card: str = Field(description="The stringified json of the agent card to be returned to the user")

class StringResponse(AgentResponse):
    response: str = Field(description="The main response to be returned to the user")


class StatusAgent[ResponseT: AgentResponse]:

    def __init__(self, system_prompt: str, name: str, api_key: str, is_routing: bool, tools: list[BaseTool]):
        response_format: type[AgentResponse]
        if is_routing:
            response_format = RoutingResponse
        else:
            response_format = StringResponse

        self.agent = create_agent(
            get_model(api_key),
            tools=tools,
            checkpointer=MemorySaver(),  # TODO replace by dynamodb
            system_prompt=system_prompt,
            response_format=response_format,
            name=name
        )

    async def __call__(self, message: str, context_id: str = None) -> ResponseT:
        config: RunnableConfig = RunnableConfig(configurable={'thread_id': context_id})
        response = await self.agent.ainvoke(LangGraphMessage(message), config)
        return response['structured_response']


class LangGraphMessage(BaseModel):
    messages: list[tuple[Literal['user'], str]]

    def __init__(self, messages: str):
        super().__init__(messages=[("user", messages)])
