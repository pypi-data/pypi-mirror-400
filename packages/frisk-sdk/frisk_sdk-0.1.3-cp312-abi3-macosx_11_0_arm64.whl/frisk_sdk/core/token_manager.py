import base64
import json
import time
import requests
import threading

from typing import Optional, Callable, Iterable
from urllib.parse import urljoin

from frisk_sdk.errors.api_response_errors import FriskBaseURLNotFoundError
from frisk_sdk.errors.configuration_errors import MissingBaseURLError
from frisk_sdk.errors.api_response_errors.raise_frisk_api_error import (
    get_frisk_api_error_from_http_status,
)


class TokenManager:
    """
    Manages access token (JWT) lifecycle:
    - Fetches token using an api_key
    - Parses JWT to extract exp
    - Refreshes token if expired or on a periodic cadence (configurable; interval is in minutes)
    """

    def __init__(
        self,
        api_key: str,
        refresh_interval_minutes: int,
        base_url: str,
        callbacks: Iterable[Callable[[str], None]],
    ):
        if not base_url:
            raise MissingBaseURLError()
        self.token_url = urljoin(base_url, "/api/agent_tokens/issue")

        self.api_key = api_key
        self.refresh_interval_seconds = max(
            60, refresh_interval_minutes * 60
        )  # minimum 60s to avoid thrash
        self._access_token: Optional[str] = None
        self._exp_epoch_s: Optional[int] = None
        self._last_refresh_epoch_s: Optional[int] = None
        # Background refresh machinery
        self._bg_thread: Optional[threading.Thread] = None
        self._bg_stop_event: Optional[threading.Event] = None
        self._lock = threading.Lock()
        self._safety_margin_s = 30  # proactively refresh if exp is within 30s
        self._callbacks = callbacks

    def fetch_access_token(self) -> str:
        """
        Obtain an access token (JWT) using the api_key via the issuer endpoint.
        Returns a JWT string; the JWT must have an `exp` claim (epoch seconds).
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            resp = requests.post(self.token_url, headers=headers, timeout=10)
        except requests.ConnectionError:
            raise FriskBaseURLNotFoundError()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to reach token issuer: {e}")

        if resp.status_code != 200:
            # try to extract message for context
            error_details = None
            try:
                error_details = resp.json()
            except Exception:
                error_details = resp.text
            raise get_frisk_api_error_from_http_status(resp.status_code, error_details)

        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            raise ValueError(f"Issuer returned invalid JSON: {e}")

        token = data.get("access_token")
        if not isinstance(token, str) or not token:
            raise ValueError("Issuer response missing 'access_token' string")
        return token

    def add_callback(self, callback: Callable[[str], None]) -> None:
        self._callbacks.append(callback)

    def _decode_jwt_payload(self, token: str) -> dict:
        """Decode a JWT without verifying signature to read payload fields like exp."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            payload_b64 = parts[1]
            # Fix base64url padding
            padding = "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            return json.loads(payload_bytes.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to decode JWT payload: {e}")

    def _update_cached_token(self, token: str) -> None:
        payload = self._decode_jwt_payload(token)
        exp = payload.get("exp")
        if not isinstance(exp, int):
            raise ValueError("JWT payload missing integer 'exp' claim")
        now = int(time.time())
        old_token = self._access_token
        self._access_token = token
        if old_token != token:
            for callback in self._callbacks:
                callback(token)

        self._exp_epoch_s = exp
        self._last_refresh_epoch_s = now

    def _needs_refresh(self, now_s: int) -> bool:
        # If no token, we need to fetch
        if (
            self._access_token is None
            or self._exp_epoch_s is None
            or self._last_refresh_epoch_s is None
        ):
            return True
        # Expired or exp reached (use strict check)
        if now_s >= self._exp_epoch_s:
            return True
        # Proactive safety margin: if exp is near, refresh early
        if (self._exp_epoch_s - now_s) <= self._safety_margin_s:
            return True
        # Periodic refresh window reached
        if (now_s - self._last_refresh_epoch_s) >= self.refresh_interval_seconds:
            return True
        return False

    def get_access_token(self) -> str:
        """
        Returns a valid access token. Refreshes if expired or refresh interval reached.
        Thread-safe: uses a lock to prevent concurrent refreshes.
        """
        now = int(time.time())
        if self._needs_refresh(now):
            with self._lock:
                # Re-check under lock to avoid duplicate fetches
                now2 = int(time.time())
                if self._needs_refresh(now2):
                    token = self.fetch_access_token()
                    self._update_cached_token(token)

        if self._access_token is None:
            raise RuntimeError("Failed to obtain access token")
        return self._access_token

    def get_token_expiry(self) -> Optional[int]:
        return self._exp_epoch_s

    def force_refresh(self) -> str:
        with self._lock:
            token = self.fetch_access_token()
            self._update_cached_token(token)
            return token

    # Background refresh support
    def start_background_refresh(self) -> None:
        """Starts a background thread that proactively refreshes the token.
        Safe to call multiple times; subsequent calls are no-ops if already running.
        """
        if self._bg_thread and self._bg_thread.is_alive():
            return
        self._bg_stop_event = threading.Event()

        def _runner():
            # First ensure we have a token
            try:
                self.get_access_token()
            except Exception:  # todo: Pass in a logger so these errors can be surfaced. https://linear.app/friskai/issue/POL-60/pass-logger-into-sdk
                # Swallow and retry later
                pass
            # Loop until stopped
            while self._bg_stop_event and not self._bg_stop_event.is_set():
                # Compute next sleep: wake up either on periodic interval or sooner if exp is near
                with self._lock:
                    now = int(time.time())
                    # default wake interval
                    nxt = self.refresh_interval_seconds
                    if self._exp_epoch_s is not None:
                        # time until safety margin before exp
                        time_until_margin = max(
                            0, (self._exp_epoch_s - self._safety_margin_s) - now
                        )
                        # choose the earlier of periodic refresh or safety margin
                        nxt = min(nxt, time_until_margin)
                        # Ensure a reasonable minimum to avoid tight loops
                        nxt = max(5, nxt)
                # Wait with stop-aware sleep
                stop = self._bg_stop_event.wait(timeout=nxt)
                if stop:
                    break
                # Try refresh if needed
                try:
                    self.get_access_token()
                except Exception:
                    # on failure, wait a short backoff
                    if (
                        self._bg_stop_event and not self._bg_stop_event.is_set()
                    ):  # todo: Pass in a logger so these errors can be surfaced. https://linear.app/friskai/issue/POL-60/pass-logger-into-sdk
                        self._bg_stop_event.wait(timeout=5)
                    continue

        self._bg_thread = threading.Thread(
            target=_runner, name="TokenManagerRefresher", daemon=True
        )
        self._bg_thread.start()

    def stop_background_refresh(self) -> None:
        """Signals the background thread to stop and waits briefly."""
        if self._bg_stop_event:
            self._bg_stop_event.set()
        if self._bg_thread and self._bg_thread.is_alive():
            # Wait up to a short grace period
            self._bg_thread.join(timeout=2)
        self._bg_thread = None
        self._bg_stop_event = None
