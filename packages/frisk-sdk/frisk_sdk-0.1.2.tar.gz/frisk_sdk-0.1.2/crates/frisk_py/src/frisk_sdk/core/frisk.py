import os
from typing import Any, Optional
from cuid2 import cuid_wrapper

from opentelemetry import propagate
from opentelemetry.propagators.textmap import CarrierT

from ..telemetry.init_tracing import init_tracing
from .._core import FriskHandle as FriskCoreHandle, ProcessToolCallResultPy

from frisk_sdk.telemetry.get_tracer import get_tracer
from .token_manager import TokenManager
from .frisk_session import FriskSession
from frisk_sdk.framework_adapter.framework_adapter import FrameworkAdapter, ToolCallInfo
from frisk_sdk.framework_adapter.base_framework_adapter import BaseFrameworkAdapter

# todo: config. https://linear.app/friskai/issue/POL-55/add-config-library-to-sdk
TOKEN_ISSUER_URL = os.getenv("FRISK_TOKEN_ISSUER_URL")
TOKEN_REFRESH_INTERVAL_MINUTES = 5


class Frisk[ToolCallT]:
    def __init__(
        self,
        api_key: str,
        framework_adapter: Optional[FrameworkAdapter[ToolCallT]] = None,
    ):
        self._framework_adapter = framework_adapter or BaseFrameworkAdapter()
        self._tracer = get_tracer()  # todo: Standardize underscored properties. https://linear.app/friskai/issue/POL-97/small-cleanup-task-tracker

        # api_key is used to obtain short-lived access tokens
        self._token_manager = TokenManager(
            api_key=api_key,
            refresh_interval_minutes=TOKEN_REFRESH_INTERVAL_MINUTES,
            issuer_url=TOKEN_ISSUER_URL,
            callbacks=[],
        )
        self._token_manager.start_background_refresh()
        self._cuid_generator = cuid_wrapper()

        # Initialize tracing with a current token (will fetch on demand)
        current_token = self._token_manager.get_access_token()
        init_tracing(current_token)
        self._handle = FriskCoreHandle(current_token)

        self._token_manager.add_callback(lambda token: self.update_access_token(token))
        self._token_manager.add_callback(lambda token: init_tracing(token))

    def create_session(self) -> "FriskSession":
        return FriskSession(self, self._tracer, self._framework_adapter)

    def update_access_token(self, access_token: str):
        self._handle.update_access_token(access_token)

    def get_tool_call_info(self, tool_call: ToolCallT) -> ToolCallInfo:
        return self._framework_adapter.get_tool_call_info(tool_call)

    def evaluate_tool_call(
        self,
        tool_name: str,
        tool_args: Optional[dict[str, Any] | str],
        agent_state: Optional[dict[str, Any] | str],
        frisk_tool_call_id: str,
        trace_context_carrier: Optional[CarrierT],
    ) -> ProcessToolCallResultPy:
        if trace_context_carrier is None:
            trace_context_carrier = {}
            propagate.inject(
                trace_context_carrier
            )  # todo: Test when trace context carrier is not explicitly set to None (but current span is active && but current span is not active). https://linear.app/friskai/issue/POL-102/python-side-policy-engine-tests

        return self._handle.process(
            tool_name,
            self._framework_adapter.serialize_tool_args(tool_args)
            if (tool_args is not None)
            else "",
            self._framework_adapter.serialize_agent_state(agent_state)
            if (agent_state is not None)
            else "",
            frisk_tool_call_id,
            trace_context_carrier,
        )

    def shutdown(self) -> None:
        # Stop background refresher if running
        self._token_manager.stop_background_refresh()
