import json
import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskStatusUpdateEvent, TaskStatus, TaskState, TaskArtifactUpdateEvent, Artifact
from a2a.utils import new_text_artifact
from langchain_core.tools import BaseTool

from .agent import StatusAgent, RoutingResponse, StringResponse

logger = logging.getLogger(__name__)

ROUTING_SYSTEM_PROMPT = """
You are a helpful routing assistant which routes user requests to specialized remote agents. Your main task is to:
1. look up available agents via their A2A agent cards
2. select the best matching agent for the user query
3. return the matching agent card for that agent."""


class RoutingAgentExecutor(AgentExecutor):

    def __init__(self, api_key: str, system_prompt: str, routing_tool: BaseTool, tools: list[BaseTool] | None = None):
        super().__init__()
        self.agent = StatusAgent[StringResponse](
            system_prompt=system_prompt,
            name="Router",
            api_key=api_key,
            is_routing=False,
            tools=[] if tools is None else tools,
        )
        self.routing_agent = StatusAgent[RoutingResponse](
            system_prompt=ROUTING_SYSTEM_PROMPT,
            name="Router",
            api_key=api_key,
            is_routing=True,
            tools=[routing_tool]
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # set status to processing
        await event_queue.enqueue_event(TaskStatusUpdateEvent(status=TaskStatus(state=TaskState.working),
                                                              final=False,
                                                              context_id=context.context_id,
                                                              task_id=context.task_id))
        agent_response: StringResponse = await self.agent(message=context.get_user_input(),
                                                          context_id=context.context_id)

        artifact: Artifact
        if agent_response.status == TaskState.rejected:
            agent_response: RoutingResponse = await self.routing_agent(message=context.get_user_input(),
                                                                       context_id=context.context_id)
            agent_name: str = json.loads(agent_response.agent_card)["name"]
            logger.info(f"Request with id {context.context_id} got rejected and will be rerouted to a '{agent_name}'.",
                        extra={"card": agent_response.agent_card})
            artifact = new_text_artifact(name='target_agent', description='New target agent for request.',
                                         text=agent_response.agent_card)
        else:
            logger.info(f"Request with id {context.context_id} was successfully processed by agent.")
            artifact = new_text_artifact(name='current_result', description='Result of request to agent.',
                                         text=agent_response.response)

        # publish actual result
        await event_queue.enqueue_event(TaskArtifactUpdateEvent(append=False,
                                                                context_id=context.context_id,
                                                                task_id=context.task_id,
                                                                last_chunk=True,
                                                                artifact=artifact))
        # set and publish the final status
        await event_queue.enqueue_event(TaskStatusUpdateEvent(status=TaskStatus(
            state=TaskState(agent_response.status)),
            final=True,
            context_id=context.context_id,
            task_id=context.task_id))
