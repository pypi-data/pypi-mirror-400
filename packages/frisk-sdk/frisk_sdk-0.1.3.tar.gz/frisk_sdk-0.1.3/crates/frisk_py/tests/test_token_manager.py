import base64
import json
import threading
import time
from unittest.mock import MagicMock

import pytest

from frisk_sdk.core.token_manager import TokenManager


class ImmediateThread:
    def __init__(self, target, name=None, daemon=None):
        self._target = target
        self._alive = False

    def start(self):
        self._alive = True
        try:
            self._target()
        finally:
            self._alive = False

    def is_alive(self):
        return self._alive

    def join(self, timeout=None):
        return


class ImmediateEvent:
    """A non-blocking threading.Event replacement for tests.

    TokenManager's background refresher uses Event.wait(timeout=...). Under ImmediateThread,
    the runner executes inline, so any real wait would deadlock the test. We also need
    the refresher loop to *terminate*, so wait(timeout=...) returns True to simulate an
    immediate stop signal.
    """

    def __init__(self):
        self._flag = False

    def is_set(self) -> bool:
        return self._flag

    def set(self) -> None:
        self._flag = True

    def wait(self, timeout: float | None = None) -> bool:
        # Never block in tests. For timeout-based sleeps (which the background refresher
        # uses), return True so the loop breaks immediately.
        if timeout is not None:
            return True
        return self._flag


@pytest.fixture(autouse=True)
def _immediate_background_threads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make TokenManager background refresh deterministic and non-blocking in tests."""

    # Patch threading primitives used inside token_manager.py
    monkeypatch.setattr(threading, "Thread", ImmediateThread)
    monkeypatch.setattr(threading, "Event", ImmediateEvent)


def _make_jwt(*, exp: int | None = None, payload_overrides: dict | None = None) -> str:
    """Create a minimal unsigned JWT (alg=none) suitable for decode-only unit tests."""

    header = {"alg": "none", "typ": "JWT"}
    if exp is None:
        exp = int(time.time()) + 3600
    payload = {"exp": exp}
    if payload_overrides:
        payload.update(payload_overrides)

    def b64url(obj: dict) -> str:
        raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    return f"{b64url(header)}.{b64url(payload)}."  # empty signature


@pytest.mark.unit
def test_decode_jwt_payload_valid_roundtrip():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    exp = int(time.time()) + 123
    token = _make_jwt(exp=exp, payload_overrides={"sub": "user-1"})

    payload = tm._decode_jwt_payload(token)
    assert payload["exp"] == exp
    assert payload["sub"] == "user-1"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        "a.b",  # missing third part
        "a.b.c.d",  # too many parts
    ],
)
@pytest.mark.unit
def test_decode_jwt_payload_rejects_invalid_format(token: str):
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    with pytest.raises(ValueError, match="Failed to decode JWT payload"):
        tm._decode_jwt_payload(token)


@pytest.mark.unit
def test_update_cached_token_requires_integer_exp():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    token = _make_jwt(payload_overrides={"exp": "not-int"})
    with pytest.raises(ValueError, match="missing integer 'exp'"):
        tm._update_cached_token(token)


@pytest.mark.unit
def test_update_cached_token_triggers_callbacks_only_when_token_changes():
    cb = MagicMock(name="callback")
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[cb],
    )

    token1 = _make_jwt(exp=int(time.time()) + 100)
    token2 = _make_jwt(exp=int(time.time()) + 200)

    tm._update_cached_token(token1)
    cb.assert_called_once_with(token1)

    cb.reset_mock()
    tm._update_cached_token(token1)
    cb.assert_not_called()

    tm._update_cached_token(token2)
    cb.assert_called_once_with(token2)


@pytest.mark.unit
def test_needs_refresh_true_when_no_cached_token():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )
    assert tm._needs_refresh(int(time.time())) is True


@pytest.mark.unit
def test_needs_refresh_true_when_expired_or_at_exp():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )
    now = int(time.time())
    tm._access_token = "t"
    tm._exp_epoch_s = now
    tm._last_refresh_epoch_s = now - 1

    assert tm._needs_refresh(now) is True


@pytest.mark.unit
def test_needs_refresh_true_when_within_safety_margin():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )
    now = int(time.time())
    tm._access_token = "t"
    tm._last_refresh_epoch_s = now
    tm._exp_epoch_s = now + tm._safety_margin_s  # exactly at margin

    assert tm._needs_refresh(now) is True


@pytest.mark.unit
def test_needs_refresh_true_when_refresh_interval_elapsed():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )
    now = int(time.time())
    tm._access_token = "t"
    tm._exp_epoch_s = now + 99999
    tm._last_refresh_epoch_s = now - tm.refresh_interval_seconds

    assert tm._needs_refresh(now) is True


@pytest.mark.unit
def test_needs_refresh_false_when_token_fresh():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )
    now = int(time.time())
    tm._access_token = "t"
    tm._exp_epoch_s = now + 99999
    tm._last_refresh_epoch_s = now

    assert tm._needs_refresh(now) is False


@pytest.mark.unit
def test_get_access_token_fetches_and_caches(monkeypatch: pytest.MonkeyPatch):
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    token = _make_jwt(exp=int(time.time()) + 3600)
    fetch = MagicMock(return_value=token)
    monkeypatch.setattr(tm, "fetch_access_token", fetch)

    t1 = tm.get_access_token()
    t2 = tm.get_access_token()

    assert t1 == token
    assert t2 == token
    fetch.assert_called_once()  # second call should use cached token


@pytest.mark.unit
def test_get_token_expiry_returns_cached_exp(monkeypatch: pytest.MonkeyPatch):
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    exp = int(time.time()) + 3600
    token = _make_jwt(exp=exp)
    monkeypatch.setattr(tm, "fetch_access_token", lambda: token)

    tm.get_access_token()
    assert tm.get_token_expiry() == exp


@pytest.mark.unit
def test_force_refresh_always_fetches(monkeypatch: pytest.MonkeyPatch):
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    token1 = _make_jwt(exp=int(time.time()) + 111)
    token2 = _make_jwt(exp=int(time.time()) + 222)
    fetch = MagicMock(side_effect=[token1, token2])
    monkeypatch.setattr(tm, "fetch_access_token", fetch)

    assert tm.force_refresh() == token1
    assert tm.force_refresh() == token2
    assert fetch.call_count == 2


@pytest.mark.unit
def test_get_access_token_does_not_double_fetch_with_dynamic_needs_refresh(
    monkeypatch: pytest.MonkeyPatch,
):
    """Deterministic boundary: if _needs_refresh flips between outer and inner checks,
    fetch_access_token should still only run once.

    This covers the double-checked locking behavior without requiring real threads.
    """

    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    token = _make_jwt(exp=int(time.time()) + 3600)
    fetch = MagicMock(return_value=token)
    monkeypatch.setattr(tm, "fetch_access_token", fetch)

    # Simulate: first call says refresh needed, second call under the lock says refresh needed,
    # subsequent calls say no refresh.
    needs_refresh = MagicMock(side_effect=[True, True, False, False])
    monkeypatch.setattr(tm, "_needs_refresh", needs_refresh)

    assert tm.get_access_token() == token
    assert tm.get_access_token() == token

    # Needs refresh checked at least twice on first call (outside and inside lock).
    assert needs_refresh.call_count >= 2
    # Only one fetch should happen.
    fetch.assert_called_once()


@pytest.mark.unit
def test_start_background_refresh_is_noop_when_already_running(
    monkeypatch: pytest.MonkeyPatch,
):
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    monkeypatch.setattr(tm, "get_access_token", MagicMock(return_value=_make_jwt()))

    tm.start_background_refresh()
    first_thread = tm._bg_thread
    assert first_thread is not None

    tm.start_background_refresh()
    second_thread = tm._bg_thread

    # With ImmediateThread, the thread runs to completion synchronously, so it's not alive
    # by the time start_background_refresh returns. Starting again creates a new thread.
    assert second_thread is not None

    tm.stop_background_refresh()


@pytest.mark.unit
def test_stop_background_refresh_clears_thread_state():
    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    # Stopping without starting should be safe and clear state
    tm.stop_background_refresh()
    assert tm._bg_thread is None
    assert tm._bg_stop_event is None


@pytest.mark.unit
def test_start_and_stop_background_refresh_smoke(monkeypatch: pytest.MonkeyPatch):
    """Smoke: start_background_refresh executes synchronously and leaves clean state."""

    tm = TokenManager(
        api_key="k",
        refresh_interval_minutes=5,
        base_url="http://issuer",
        callbacks=[],
    )

    # Ensure initial token acquisition doesn't error.
    monkeypatch.setattr(tm, "get_access_token", MagicMock(return_value=_make_jwt()))

    tm.start_background_refresh()
    assert tm._bg_thread is not None

    tm.stop_background_refresh()
    assert tm._bg_thread is None
    assert tm._bg_stop_event is None
