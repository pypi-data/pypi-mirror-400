import os
import time
import base64
import json
import pytest
from unittest.mock import MagicMock

from frisk_sdk.core.frisk import Frisk


# Helpers to produce a minimal valid JWT with future exp
def make_jwt(exp_epoch_s: int | None = None) -> str:
    header = {"alg": "none", "typ": "JWT"}
    if exp_epoch_s is None:
        exp_epoch_s = int(time.time()) + 3600
    payload = {"exp": exp_epoch_s}

    def b64url(d: dict) -> str:
        raw = json.dumps(d, separators=(",", ":")).encode("utf-8")
        s = base64.urlsafe_b64encode(raw).decode("utf-8")
        return s.rstrip("=")

    return f"{b64url(header)}.{b64url(payload)}."  # empty signature is fine for decode-only


@pytest.fixture(autouse=True)
def suppress_rust_warn_logs(monkeypatch):
    # Suppress tracing::warn from Rust by raising the log level
    monkeypatch.setenv("RUST_LOG", "error")
    yield


@pytest.fixture(autouse=True)
def mock_token_manager(monkeypatch):
    # Ensure issuer URL presence doesn't trigger real network
    os.environ.setdefault("FRISK_TOKEN_ISSUER_URL", "http://example.local/issuer")

    # Monkeypatch TokenManager.fetch_access_token to avoid HTTP calls
    from frisk_sdk.core.token_manager import TokenManager

    def fake_fetch(self):
        return make_jwt()

    monkeypatch.setattr(TokenManager, "fetch_access_token", fake_fetch)
    yield


@pytest.fixture
def frisk_instance():
    # Create Frisk; TokenManager is already mocked to return a valid JWT
    f = Frisk(api_key="test_api_key")
    yield f
    # Stop background refresher
    f.shutdown()


@pytest.mark.integration
def test_evaluate_tool_call_allow_when_no_policies(frisk_instance):
    # With no policies loaded yet, engine should allow by default
    res = frisk_instance.evaluate_tool_call(
        tool_name="unknown_tool",
        tool_args={"a": 1},
        agent_state={"user": {"id": 123}},
        frisk_tool_call_id="call-1",
        trace_context_carrier=None,  # exercise injection path
    )
    assert res.decision == "allow"
    assert res.rules_matched_count == 0
    assert res.reason is None


@pytest.mark.integration
def test_evaluate_tool_call_with_trace_context(frisk_instance):
    # Providing a trace context carrier should be accepted by rust side
    carrier = {}
    res = frisk_instance.evaluate_tool_call(
        tool_name="another_tool",
        tool_args={"x": 42},
        agent_state={"user": {"isAdmin": False}},
        frisk_tool_call_id="call-2",
        trace_context_carrier=carrier,
    )
    assert res.decision in {
        "allow",
        "deny",
    }  # depending on policies; with none it's allow
    assert isinstance(res.rules_matched_count, int)


@pytest.mark.integration
def test_evaluate_tool_call_none_args_state_raises(frisk_instance):
    # Boundary: passing None leads to empty strings to rust, which fails JSON parsing
    with pytest.raises(ValueError) as excinfo:
        frisk_instance.evaluate_tool_call(
            tool_name="tool_x",
            tool_args=None,
            agent_state=None,
            frisk_tool_call_id="call-3",
            trace_context_carrier={},
        )
    # The PyO3 layer raises PyValueError -> mapped as ValueError in Python
    assert "Invalid tool_args JSON" in str(
        excinfo.value
    ) or "Invalid agent_state JSON" in str(excinfo.value)


@pytest.mark.integration
def test_update_access_token_delegates_to_core_handle(monkeypatch):
    """Boundary/unit: verify Python forwards the token to the underlying core handle."""

    from frisk_sdk.core import frisk as frisk_module

    # Avoid wiring real OpenTelemetry providers
    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    # Keep TokenManager from doing any real work.
    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.stop_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    # Mock the Rust/PyO3 handle and capture initialization.
    core_handle = MagicMock(name="FriskCoreHandle")

    def _handle_factory(current_token: str):
        assert (
            current_token == make_jwt()
        )  # ensures Frisk passes through the fetched token
        return core_handle

    monkeypatch.setattr(frisk_module, "FriskCoreHandle", _handle_factory)

    f = Frisk(api_key="test_api_key")
    try:
        f.update_access_token("new-token")
        core_handle.update_access_token.assert_called_once_with("new-token")
    finally:
        f.shutdown()


@pytest.mark.integration
def test_update_access_token_accepts_empty_string(monkeypatch):
    """Boundary/unit: empty string should be forwarded unchanged (core decides validity)."""

    from frisk_sdk.core import frisk as frisk_module

    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.stop_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    f = Frisk(api_key="test_api_key")
    try:
        f.update_access_token("")
        core_handle.update_access_token.assert_called_once_with("")
    finally:
        f.shutdown()


@pytest.mark.integration
def test_shutdown_stops_background_refresh(monkeypatch):
    """Boundary/unit: shutdown should always stop the background token refresh loop."""

    from frisk_sdk.core import frisk as frisk_module

    # Avoid wiring real OpenTelemetry providers
    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    f = Frisk(api_key="test_api_key")

    # Act
    f.shutdown()

    # Assert
    token_manager.stop_background_refresh.assert_called_once_with()


@pytest.mark.integration
def test_shutdown_is_idempotent(monkeypatch):
    """Boundary/unit: calling shutdown twice should call stop twice (no internal guard)."""

    from frisk_sdk.core import frisk as frisk_module

    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    f = Frisk(api_key="test_api_key")

    f.shutdown()
    f.shutdown()

    assert token_manager.stop_background_refresh.call_count == 2


@pytest.mark.integration
def test_shutdown_propagates_token_manager_errors(monkeypatch):
    """Boundary/unit: errors from TokenManager.stop_background_refresh should bubble up."""

    from frisk_sdk.core import frisk as frisk_module

    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    token_manager.stop_background_refresh.side_effect = RuntimeError("stop failed")
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    f = Frisk(api_key="test_api_key")

    with pytest.raises(RuntimeError, match="stop failed"):
        f.shutdown()


@pytest.mark.unit
def test_create_session_returns_frisk_session_wired_to_frisk(monkeypatch):
    """Boundary/unit: create_session should return a FriskSession bound to this Frisk instance."""

    from frisk_sdk.core import frisk as frisk_module

    # Avoid wiring real OpenTelemetry providers
    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    # Make tracer deterministic and easy to compare.
    tracer = object()
    monkeypatch.setattr(frisk_module, "get_tracer", lambda: tracer)

    # TokenManager stub
    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.stop_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    # Core handle stub
    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    f = Frisk(api_key="test_api_key")
    try:
        session = f.create_session()

        from frisk_sdk.core.frisk_session import FriskSession

        assert isinstance(session, FriskSession)
        assert session.frisk is f
        assert session.tracer is tracer
        # Default path should use BaseFrameworkAdapter
        from frisk_sdk.framework_adapter.base_framework_adapter import (
            BaseFrameworkAdapter,
        )

        assert isinstance(session.framework_adapter, BaseFrameworkAdapter)
    finally:
        f.shutdown()


class _DummyAdapter:
    def __init__(self, tool_call_info=None, *, raise_exc: Exception | None = None):
        self._tool_call_info = tool_call_info
        self._raise_exc = raise_exc
        self.calls: list[object] = []

    def serialize_tool_args(self, tool_args):
        return json.dumps(tool_args)

    def serialize_agent_state(self, agent_state):
        return json.dumps(agent_state)

    def get_tool_call_info(self, tool_call):
        self.calls.append(tool_call)
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._tool_call_info


@pytest.mark.unit
def test_create_session_uses_provided_framework_adapter(monkeypatch):
    """Boundary/unit: a provided framework_adapter should be used by the created session."""

    from frisk_sdk.core import frisk as frisk_module

    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    tracer = object()
    monkeypatch.setattr(frisk_module, "get_tracer", lambda: tracer)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.stop_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    custom_adapter = _DummyAdapter(tool_call_info=None)

    f = Frisk(api_key="test_api_key", framework_adapter=custom_adapter)
    try:
        session = f.create_session()

        assert session.framework_adapter is custom_adapter
        assert session.frisk is f
        assert session.tracer is tracer
    finally:
        f.shutdown()


@pytest.mark.unit
def test_get_tool_call_info_delegates_to_framework_adapter(monkeypatch):
    """Boundary/unit: get_tool_call_info should delegate to the configured adapter."""

    from frisk_sdk.core import frisk as frisk_module

    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.stop_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    from frisk_sdk.framework_adapter.framework_adapter import ToolCallInfo

    expected = ToolCallInfo(id="id-1", name="tool", args={"x": 1})
    adapter = _DummyAdapter(tool_call_info=expected)

    tool_call = object()

    f = Frisk(api_key="test_api_key", framework_adapter=adapter)
    try:
        res = f.get_tool_call_info(tool_call)

        assert res == expected
        assert adapter.calls == [tool_call]
    finally:
        f.shutdown()


@pytest.mark.unit
def test_get_tool_call_info_propagates_adapter_errors(monkeypatch):
    """Boundary/unit: adapter failures should bubble up unchanged."""

    from frisk_sdk.core import frisk as frisk_module

    monkeypatch.setattr(frisk_module, "init_tracing", lambda *_a, **_kw: None)

    token_manager = MagicMock(name="TokenManager")
    token_manager.get_access_token.return_value = make_jwt()
    token_manager.start_background_refresh.return_value = None
    token_manager.stop_background_refresh.return_value = None
    token_manager.add_callback.return_value = None
    monkeypatch.setattr(
        frisk_module, "TokenManager", lambda *args, **kwargs: token_manager
    )

    core_handle = MagicMock(name="FriskCoreHandle")
    monkeypatch.setattr(frisk_module, "FriskCoreHandle", lambda *_a, **_kw: core_handle)

    adapter = _DummyAdapter(tool_call_info=None, raise_exc=ValueError("bad tool call"))
    tool_call = object()

    f = Frisk(api_key="test_api_key", framework_adapter=adapter)
    try:
        with pytest.raises(ValueError, match="bad tool call"):
            f.get_tool_call_info(tool_call)
        assert adapter.calls == [tool_call]
    finally:
        f.shutdown()
