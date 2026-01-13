from dataclasses import dataclass
from typing import Protocol, TypeVar, Any

ToolCallT = TypeVar("ToolCallT", contravariant=True)


@dataclass(frozen=True)
class ToolCallInfo:
    id: str
    name: str
    args: dict[str, Any]


class FrameworkAdapter(Protocol[ToolCallT]):
    def serialize_tool_args(self, tool_args: dict[str, Any]) -> str: ...
    def serialize_agent_state(self, agent_state: dict[str, Any]) -> str: ...
    def get_tool_call_info(self, tool_call: ToolCallT) -> ToolCallInfo: ...
