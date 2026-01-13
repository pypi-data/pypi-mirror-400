from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

from opentelemetry.propagators.textmap import CarrierT
from opentelemetry.sdk.trace import Span
from opentelemetry.trace import Tracer
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from cuid2 import cuid_wrapper

from opentelemetry import trace

from .._core import ProcessToolCallResultPy
from frisk_sdk.framework_adapter.framework_adapter import FrameworkAdapter, ToolCallInfo
from .tool_call_span import ToolCallSpan

if TYPE_CHECKING:
    from .frisk import Frisk


class FriskSession[ToolCallT]:
    def __init__(
        self,
        frisk: Frisk,
        tracer: Tracer,
        framework_adapter: FrameworkAdapter[ToolCallT],
    ):
        self.root_span: Optional[Span] = None
        self.frisk = frisk
        self.tracer = tracer
        self._cuid_generator = cuid_wrapper()
        self.framework_adapter = framework_adapter
        # Deprecated: per-call tracking now handled by ToolCallSpan
        self.tool_call_spans = {}
        self.tool_call_start_times = {}

    def init_tracing(self, run_id: str, inputs: Dict[str, Any]) -> Span:
        self._root_run_id = run_id
        span = self.tracer.start_span("frisk_session")
        span.set_attribute(
            "user_query", self.framework_adapter.serialize_agent_state(inputs)
        )
        self.set_root_span(span)
        return span

    def end_tracing(self):
        if self.root_span:
            print("Closing root span")
            self.root_span.end()

    def set_root_span(self, span: Span) -> None:
        self.root_span = span  # todo: prevent override. https://linear.app/friskai/issue/POL-95/encapsulate-all-otel-span-creation-into-frisk-session

    def get_root_span(self) -> Span:
        return self.root_span

    def generate_tool_call_id(self) -> str:
        return self._cuid_generator()

    def evaluate_tool_call(
        self, tool_call_info: ToolCallInfo, agent_state: dict[str, Any]
    ) -> ProcessToolCallResultPy:
        with ToolCallSpan(
            self.framework_adapter,
            tool_call_info,
            agent_state,
            self.get_root_span(),
            self.tracer,
        ) as tool_span:
            span_context = trace.set_span_in_context(tool_span.span)
            trace_context_carrier: CarrierT = {}
            TraceContextTextMapPropagator().inject(
                trace_context_carrier, context=span_context
            )

            process_tool_call_result = self.frisk.evaluate_tool_call(
                tool_call_info.name,
                tool_call_info.args,
                agent_state,
                tool_call_info.id,
                trace_context_carrier,
            )

            tool_span.save_result(process_tool_call_result)
            return process_tool_call_result
