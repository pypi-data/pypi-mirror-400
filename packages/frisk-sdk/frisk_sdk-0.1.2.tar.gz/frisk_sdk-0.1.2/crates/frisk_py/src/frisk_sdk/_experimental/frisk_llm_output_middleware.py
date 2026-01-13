from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain.agents.middleware.types import ModelCallResult
from langchain_core.messages import BaseMessageChunk
from langgraph.runtime import Runtime
from typing import Any, Callable, Awaitable

from .rewriting_chat_model import (
    RewritingChatModel,
)


class FriskLLMOutputMiddleware(AgentMiddleware):
    async def abefore_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        print(f"About to call model with {len(state['messages'])} messages")
        most_recent_message: BaseMessageChunk = state["messages"][-1]
        print(
            f"Before model - Most recent message ({most_recent_message.type}): {most_recent_message.content}"
        )
        return None

    async def aafter_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        most_recent_message: BaseMessageChunk = state["messages"][-1]
        print(
            f"After model - Most recent message ({most_recent_message.type}): {most_recent_message.content}"
        )
        return None

    async def abefore_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        most_recent_message: BaseMessageChunk = state["messages"][-1]
        print(
            f"Before agent - Most recent message ({most_recent_message.type}): {most_recent_message.content}"
        )
        return None

    async def aafter_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        most_recent_message: BaseMessageChunk = state["messages"][-1]
        print(
            f"After agent - Most recent message ({most_recent_message.type}): {most_recent_message.content}"
        )
        return None

    def wrap_model_call(
        self, request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelCallResult:
        request.model = RewritingChatModel(request.model, lambda s: s.upper())
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        # most_recent_message_from_messages: BaseMessageChunk = (request.messages[-1] if request.messages else None)
        # print(f"Wrap model call - Most recent message from messages ({most_recent_message_from_messages.type}): {most_recent_message_from_messages.content}")
        # most_recent_message_from_state: BaseMessageChunk = request.state['messages'][-1]
        # print(f"Wrap model call - Most recent message from state ({most_recent_message_from_state.type}): {most_recent_message_from_messages.content}")

        request.model = RewritingChatModel(request.model, lambda s: s.upper())
        return await handler(request)
