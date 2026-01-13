import json
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from frisk_sdk.framework_adapter.framework_adapter import ToolCallInfo
from frisk_sdk.core.frisk_session import FriskSession


class _DummyAdapter:
    def serialize_tool_args(self, tool_args):
        return json.dumps(tool_args)

    def serialize_agent_state(self, agent_state):
        return json.dumps(agent_state)

    def get_tool_call_info(self, tool_call):
        raise NotImplementedError


@dataclass
class _DummyResult:
    decision: str = "allow"
    rules_matched_count: int = 0
    reason: str | None = None


@pytest.mark.unit
def test_init_tracing_sets_root_span_and_user_query_attribute(
    monkeypatch: pytest.MonkeyPatch,
):
    adapter = _DummyAdapter()

    span = MagicMock(name="Span")
    tracer = MagicMock(name="Tracer")
    tracer.start_span.return_value = span

    frisk_handle = MagicMock(name="Frisk")

    s = FriskSession(frisk=frisk_handle, tracer=tracer, framework_adapter=adapter)

    inputs = {"prompt": "hi"}
    returned_span = s.init_tracing(run_id="run-1", inputs=inputs)

    assert returned_span is span
    assert s.get_root_span() is span

    tracer.start_span.assert_called_once_with("frisk_session")
    span.set_attribute.assert_called_once_with("user_query", json.dumps(inputs))


@pytest.mark.unit
def test_end_tracing_ends_root_span_when_present(capsys):
    adapter = _DummyAdapter()
    tracer = MagicMock(name="Tracer")
    frisk_handle = MagicMock(name="Frisk")
    s = FriskSession(frisk=frisk_handle, tracer=tracer, framework_adapter=adapter)

    span = MagicMock(name="Span")
    s.set_root_span(span)

    s.end_tracing()

    out = capsys.readouterr().out
    assert "Closing root span" in out
    span.end.assert_called_once_with()


@pytest.mark.unit
def test_end_tracing_noop_when_no_root_span(capsys):
    adapter = _DummyAdapter()
    tracer = MagicMock(name="Tracer")
    frisk_handle = MagicMock(name="Frisk")
    s = FriskSession(frisk=frisk_handle, tracer=tracer, framework_adapter=adapter)

    s.end_tracing()

    out = capsys.readouterr().out
    assert out == ""


@pytest.mark.unit
def test_generate_tool_call_id_uses_cuid_generator(monkeypatch: pytest.MonkeyPatch):
    adapter = _DummyAdapter()
    tracer = MagicMock(name="Tracer")
    frisk_handle = MagicMock(name="Frisk")

    s = FriskSession(frisk=frisk_handle, tracer=tracer, framework_adapter=adapter)
    s._cuid_generator = lambda: "cuid-123"  # boundary: deterministic ID

    assert s.generate_tool_call_id() == "cuid-123"


@pytest.mark.integration
def test_evaluate_tool_call_injects_trace_context_and_delegates(
    monkeypatch: pytest.MonkeyPatch,
):
    adapter = _DummyAdapter()

    tracer = MagicMock(name="Tracer")
    frisk_handle = MagicMock(name="Frisk")
    expected = _DummyResult(decision="allow", rules_matched_count=2, reason=None)
    frisk_handle.evaluate_tool_call.return_value = expected

    # Patch ToolCallSpan to avoid OpenTelemetry and to assert wiring.
    import frisk_sdk.core.frisk_session as session_module

    tool_span_cm = MagicMock(name="ToolCallSpanCM")
    tool_span_cm.__enter__.return_value = tool_span_cm
    tool_span_cm.__exit__.return_value = False
    tool_span_cm.span = object()

    tool_call_span_ctor = MagicMock(return_value=tool_span_cm)
    monkeypatch.setattr(session_module, "ToolCallSpan", tool_call_span_ctor)

    # Make tracing context injection deterministic.
    inject = MagicMock(name="inject")
    monkeypatch.setattr(session_module.TraceContextTextMapPropagator, "inject", inject)

    span_ctx = object()
    monkeypatch.setattr(
        session_module.trace, "set_span_in_context", lambda _span: span_ctx
    )

    s = FriskSession(frisk=frisk_handle, tracer=tracer, framework_adapter=adapter)

    tool_call_info = ToolCallInfo(id="toolcall-1", name="tool_a", args={"x": 1})
    agent_state = {"user": {"id": 1}}

    res = s.evaluate_tool_call(tool_call_info, agent_state)

    assert res is expected

    tool_call_span_ctor.assert_called_once()
    frisk_handle.evaluate_tool_call.assert_called_once()

    called_args = frisk_handle.evaluate_tool_call.call_args.args
    assert called_args[0] == "tool_a"
    assert called_args[1] == {"x": 1}
    assert called_args[2] == agent_state
    assert called_args[3] == "toolcall-1"

    # A carrier dict should be passed through and injected into.
    carrier = called_args[4]
    assert isinstance(carrier, dict)

    inject.assert_called_once()
    assert inject.call_args.kwargs["context"] is span_ctx

    tool_span_cm.save_result.assert_called_once_with(expected)


@pytest.mark.unit
def test_evaluate_tool_call_propagates_exceptions(monkeypatch: pytest.MonkeyPatch):
    adapter = _DummyAdapter()
    tracer = MagicMock(name="Tracer")
    frisk_handle = MagicMock(name="Frisk")

    import frisk_sdk.core.frisk_session as session_module

    # ToolCallSpan context manager that lets exceptions propagate (like the real one).
    tool_span_cm = MagicMock(name="ToolCallSpanCM")
    tool_span_cm.__enter__.return_value = tool_span_cm
    tool_span_cm.__exit__.return_value = False
    tool_span_cm.span = object()

    monkeypatch.setattr(
        session_module, "ToolCallSpan", MagicMock(return_value=tool_span_cm)
    )
    monkeypatch.setattr(
        session_module.TraceContextTextMapPropagator, "inject", MagicMock()
    )
    monkeypatch.setattr(
        session_module.trace, "set_span_in_context", lambda _span: object()
    )

    frisk_handle.evaluate_tool_call.side_effect = ValueError("boom")

    s = FriskSession(frisk=frisk_handle, tracer=tracer, framework_adapter=adapter)
    tool_call_info = ToolCallInfo(id="toolcall-1", name="tool_a", args={"x": 1})

    with pytest.raises(ValueError, match="boom"):
        s.evaluate_tool_call(tool_call_info, {"user": 1})

    # save_result should not be called if evaluate_tool_call raises
    tool_span_cm.save_result.assert_not_called()
