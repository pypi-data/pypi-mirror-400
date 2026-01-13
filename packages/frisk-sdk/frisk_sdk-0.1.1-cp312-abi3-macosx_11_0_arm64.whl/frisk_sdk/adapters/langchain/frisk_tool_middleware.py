from __future__ import annotations
import asyncio

import pydash
from langchain.agents.middleware import (
    AgentMiddleware,
)
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage, AIMessage
from typing import Callable, Coroutine

from langgraph.types import Command

from cuid2 import cuid_wrapper

from ... import ProcessToolCallResultPy
from ...core import Frisk
from frisk_sdk.framework_adapter.framework_adapter import ToolCallInfo


class FriskToolMiddleware(AgentMiddleware):
    def __init__(self, frisk: Frisk):
        self._frisk_handle: Frisk = frisk
        self._cuid_generator = cuid_wrapper()
        self._tracer = frisk._tracer

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        return asyncio.run(self.awrap_tool_call(request, handler))

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        initial_tool = request.tool

        if initial_tool is None:
            """
              todo: When combined with the LLMOutputMiddleware, there's always an extra "empty" tool call. Figure out why this happens and fix it.
              https://linear.app/friskai/issue/SDK-24/fix-issues-in-llm-output-middleware
            """
            return Command(update={})

        initial_tool_call = request.tool_call
        tool_call_info = self._frisk_handle._framework_adapter.get_tool_call_info(
            initial_tool_call
        )
        try:
            frisk_session = request.runtime.context.get("frisk_session", None)
            process_tool_call_result = frisk_session.evaluate_tool_call(
                tool_call_info, pydash.omit(request.state, ["messages"])
            )

            return await self.block_or_execute_tool_call(
                tool_call_info, request, handler, process_tool_call_result
            )
        except Exception as e:
            print(f"Tool failed: {e}")
            raise

    async def block_or_execute_tool_call(
        self,
        tool_call_info: ToolCallInfo,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
        process_tool_call_result: ProcessToolCallResultPy,
    ):
        if process_tool_call_result.decision == "deny":
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=process_tool_call_result.reason,
                            tool_call_id=tool_call_info.id,
                            name=tool_call_info.name,
                        ),
                        AIMessage(content=process_tool_call_result.reason),
                    ]
                }
            )
        handler_result = handler(request)
        if isinstance(handler_result, Coroutine):
            return await handler_result
        return handler_result
