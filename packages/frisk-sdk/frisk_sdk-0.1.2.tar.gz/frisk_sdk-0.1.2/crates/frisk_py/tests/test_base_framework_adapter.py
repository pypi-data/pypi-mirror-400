import json
from dataclasses import dataclass

import pytest

from frisk_sdk.framework_adapter.base_framework_adapter import BaseFrameworkAdapter
from frisk_sdk.framework_adapter.framework_adapter import ToolCallInfo


@dataclass
class _DummyToolCall:
    name: str
    args: dict


def test_serialize_tool_args_roundtrip():
    adapter = BaseFrameworkAdapter()

    tool_args = {"a": 1, "nested": {"b": True}, "list": [1, 2, 3]}
    s = adapter.serialize_tool_args(tool_args)

    assert isinstance(s, str)
    assert json.loads(s) == tool_args


def test_serialize_agent_state_roundtrip():
    adapter = BaseFrameworkAdapter()

    agent_state = {"user": {"id": 123, "role": "admin"}, "flags": ["x"]}
    s = adapter.serialize_agent_state(agent_state)

    assert isinstance(s, str)
    assert json.loads(s) == agent_state


def test_get_tool_call_info_extracts_fields_and_generates_id(
    monkeypatch: pytest.MonkeyPatch,
):
    adapter = BaseFrameworkAdapter()

    # Make id generation deterministic
    adapter._cuid_generator = lambda: "cuid-123"

    tool_call = _DummyToolCall(name="tool_a", args={"x": 1})

    info = adapter.get_tool_call_info(tool_call)

    assert isinstance(info, ToolCallInfo)
    assert info.id == "cuid-123"
    assert info.name == "tool_a"
    assert info.args == {"x": 1}


def test_get_tool_call_info_generates_unique_ids_by_default():
    adapter = BaseFrameworkAdapter()

    tool_call = _DummyToolCall(name="tool_a", args={})

    id1 = adapter.get_tool_call_info(tool_call).id
    id2 = adapter.get_tool_call_info(tool_call).id

    # cuid2 should mint distinct ids across calls
    assert isinstance(id1, str) and id1
    assert isinstance(id2, str) and id2
    assert id1 != id2
