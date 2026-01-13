import json
from typing import Any

from langchain_core.load import dumps
from langchain_core.messages import ToolCall

from ...core import Frisk as CoreFrisk
from frisk_sdk.framework_adapter.framework_adapter import FrameworkAdapter, ToolCallInfo


class LangchainFrameworkAdapter(FrameworkAdapter[ToolCall]):
    def serialize_tool_args(self, tool_args: dict[str, Any]):
        return json.dumps(tool_args)

    def serialize_agent_state(self, agent_state: dict[str, Any]):
        return dumps(agent_state)

    def get_tool_call_info(self, tool_call: ToolCall):
        return ToolCallInfo(
            id=self.get_or_create_tool_call_id(tool_call),
            name=self.get_tool_name(tool_call),
            args=tool_call["args"],
        )

    def get_or_create_tool_call_id(self, tool_call: ToolCall) -> str:
        return getattr(tool_call, "id", None) or (
            tool_call.get("id")
            if isinstance(tool_call, dict)
            else self._cuid_generator()
        )

    def get_tool_name(self, tool_call: ToolCall):
        return getattr(tool_call, "name", None) or (
            tool_call.get("name") if isinstance(tool_call, dict) else None
        )


def Frisk(api_key: str):
    return CoreFrisk(api_key, LangchainFrameworkAdapter())
