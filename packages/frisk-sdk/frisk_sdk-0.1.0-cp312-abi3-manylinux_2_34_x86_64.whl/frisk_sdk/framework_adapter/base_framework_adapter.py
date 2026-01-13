import json
from typing import Any

from cuid2 import cuid_wrapper

from frisk_sdk.framework_adapter.framework_adapter import (
    FrameworkAdapter,
    ToolCallT,
    ToolCallInfo,
)


# todo: Wrap base adapter in try-catch so that if someone imports the wrong one, they get a helpful message: "Did you forget to use an adapter"? https://linear.app/friskai/issue/POL-97/small-cleanup-task-tracker
class BaseFrameworkAdapter(FrameworkAdapter):
    def __init__(self):
        self._cuid_generator = cuid_wrapper()

    def serialize_tool_args(self, tool_args: dict[str, Any]) -> str:
        return json.dumps(tool_args)

    def serialize_agent_state(self, agent_state: dict[str, Any]) -> str:
        return json.dumps(agent_state)

    def get_tool_call_info(self, tool_call: ToolCallT) -> ToolCallInfo:
        return ToolCallInfo(
            id=self._cuid_generator(), name=tool_call.name, args=tool_call.args
        )
