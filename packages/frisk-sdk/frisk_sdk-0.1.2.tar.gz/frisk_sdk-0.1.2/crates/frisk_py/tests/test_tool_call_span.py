import json
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from frisk_sdk.framework_adapter.framework_adapter import ToolCallInfo
from frisk_sdk.core.tool_call_span import ToolCallSpan


class _DummyAdapter:
    def serialize_tool_args(self, tool_args):
        return json.dumps(tool_args)

    def serialize_agent_state(self, agent_state):
        return json.dumps(agent_state)

    def get_tool_call_info(self, tool_call):
        raise NotImplementedError


@dataclass
class _DummyResult:
    decision: str
    rules_matched_count: int
    reason: str | None = None


def test_enter_starts_span_with_expected_attributes_and_parent_context(
    monkeypatch: pytest.MonkeyPatch,
):
    adapter = _DummyAdapter()

    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})
    agent_state = {"user": {"id": 1}}

    parent_span = MagicMock(name="ParentSpan")
    parent_ctx = object()

    # Patch trace.set_span_in_context to ensure parent context wiring
    import frisk_sdk.core.tool_call_span as module

    monkeypatch.setattr(module.trace, "set_span_in_context", lambda span: parent_ctx)

    # Deterministic time for start_time_ns
    monkeypatch.setattr(module.time, "perf_counter_ns", lambda: 100)

    span = MagicMock(name="Span")
    tracer = MagicMock(name="Tracer")
    tracer.start_span.return_value = span

    # Avoid interacting with real OpenTelemetry global state
    use_span = MagicMock(name="use_span")
    monkeypatch.setattr(module, "use_span", use_span)

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state=agent_state,
        parent_span=parent_span,  # truthy => should set parent context
        tracer=tracer,
    )

    entered = tcs.__enter__()

    assert entered is tcs
    assert tcs.span is span
    assert tcs.start_time_ns == 100

    tracer.start_span.assert_called_once()
    _, kwargs = tracer.start_span.call_args

    assert kwargs["context"] is parent_ctx

    attrs = kwargs["attributes"]
    assert attrs["tool_name"] == "tool_a"
    assert attrs["tool_args"] == json.dumps({"x": 1})
    assert attrs["tool_call_id"] == "tc-1"
    assert attrs["agent_state"] == json.dumps(agent_state)

    use_span.assert_called_once_with(span)


def test_enter_with_no_parent_span_passes_none_context(monkeypatch: pytest.MonkeyPatch):
    adapter = _DummyAdapter()

    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})
    agent_state = {"user": {"id": 1}}

    import frisk_sdk.core.tool_call_span as module

    # If parent_span is falsy, set_span_in_context shouldn't be used.
    set_span_in_context = MagicMock(name="set_span_in_context")
    monkeypatch.setattr(module.trace, "set_span_in_context", set_span_in_context)

    monkeypatch.setattr(module.time, "perf_counter_ns", lambda: 100)

    span = MagicMock(name="Span")
    tracer = MagicMock(name="Tracer")
    tracer.start_span.return_value = span

    monkeypatch.setattr(module, "use_span", MagicMock())

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state=agent_state,
        parent_span=falsy_parent_span,
        tracer=tracer,
    )

    tcs.__enter__()

    _, kwargs = tracer.start_span.call_args
    assert kwargs["context"] is None
    set_span_in_context.assert_not_called()


def test_save_result_sets_decision_matched_rules_and_optional_reason(
    monkeypatch: pytest.MonkeyPatch,
):
    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    tracer = MagicMock(name="Tracer")

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=tracer,
    )

    span = MagicMock(name="Span")
    tcs.span = span

    result = _DummyResult(decision="deny", rules_matched_count=3, reason="nope")
    tcs.save_result(result)

    span.set_attributes.assert_called_once_with(
        {"decision": "deny", "matched_rules": 3}
    )
    span.set_attribute.assert_called_once_with("reason", "nope")


def test_save_result_no_reason_does_not_set_reason(monkeypatch: pytest.MonkeyPatch):
    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    tracer = MagicMock(name="Tracer")

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=tracer,
    )

    span = MagicMock(name="Span")
    tcs.span = span

    result = _DummyResult(decision="allow", rules_matched_count=0, reason=None)
    tcs.save_result(result)

    span.set_attributes.assert_called_once_with(
        {"decision": "allow", "matched_rules": 0}
    )
    span.set_attribute.assert_not_called()


def test_save_result_is_noop_when_span_is_missing():
    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=MagicMock(name="Tracer"),
    )

    # No span set => should not raise
    tcs.save_result(_DummyResult(decision="allow", rules_matched_count=0, reason=None))


def test_exit_records_latency_and_ends_span(monkeypatch: pytest.MonkeyPatch):
    import frisk_sdk.core.tool_call_span as module

    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=MagicMock(name="Tracer"),
    )

    span = MagicMock(name="Span")
    tcs.span = span
    tcs.start_time_ns = 100

    monkeypatch.setattr(module.time, "perf_counter_ns", lambda: 175)

    # No exception
    suppress = tcs.__exit__(None, None, None)

    assert suppress is False
    span.set_attribute.assert_called_once_with("latency_ns", 75)
    span.end.assert_called_once_with()


def test_exit_tags_error_and_ends_span(monkeypatch: pytest.MonkeyPatch):
    import frisk_sdk.core.tool_call_span as module

    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=MagicMock(name="Tracer"),
    )

    span = MagicMock(name="Span")
    tcs.span = span
    tcs.start_time_ns = 10

    monkeypatch.setattr(module.time, "perf_counter_ns", lambda: 20)

    exc = ValueError("boom")
    suppress = tcs.__exit__(ValueError, exc, None)

    assert suppress is False

    # latency always recorded
    span.set_attribute.assert_any_call("latency_ns", 10)
    span.set_attribute.assert_any_call("error.type", str(ValueError))
    span.set_attribute.assert_any_call("error.message", "boom")
    span.end.assert_called_once_with()


def test_exit_handles_exception_with_no_message(monkeypatch: pytest.MonkeyPatch):
    import frisk_sdk.core.tool_call_span as module

    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=MagicMock(name="Tracer"),
    )

    span = MagicMock(name="Span")
    tcs.span = span
    tcs.start_time_ns = 10

    monkeypatch.setattr(module.time, "perf_counter_ns", lambda: 20)

    suppress = tcs.__exit__(RuntimeError, None, None)

    assert suppress is False
    span.set_attribute.assert_any_call("error.message", "Unknown error")
    span.end.assert_called_once_with()


def test_exit_is_noop_when_span_missing():
    adapter = _DummyAdapter()
    tool_call_info = ToolCallInfo(id="tc-1", name="tool_a", args={"x": 1})

    falsy_parent_span = MagicMock(name="FalsyParentSpan")
    falsy_parent_span.__bool__.return_value = False

    tcs = ToolCallSpan(
        framework_adapter=adapter,
        tool_call_info=tool_call_info,
        agent_state={},
        parent_span=falsy_parent_span,
        tracer=MagicMock(name="Tracer"),
    )

    assert tcs.__exit__(None, None, None) is False
