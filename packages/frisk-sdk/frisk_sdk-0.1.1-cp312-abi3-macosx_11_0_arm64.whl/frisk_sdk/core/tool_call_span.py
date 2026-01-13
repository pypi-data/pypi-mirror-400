import time
from typing import Dict, Any, Optional

from frisk_sdk import ProcessToolCallResultPy
from opentelemetry import trace
from opentelemetry.sdk.trace import Span
from opentelemetry.trace import Tracer, use_span

from frisk_sdk.framework_adapter.framework_adapter import FrameworkAdapter, ToolCallInfo


class ToolCallSpan:
    """
    Context manager wrapping an OpenTelemetry span for a single tool call.
    - __enter__: starts the span with initial attributes
    - close(...): sets decision-related attributes and ends the span
    - __exit__: ensures span ends even on exception
    """

    def __init__(
        self,
        framework_adapter: FrameworkAdapter,
        tool_call_info: ToolCallInfo,
        agent_state: Dict[str, Any],
        parent_span: Span,
        tracer: Tracer,
    ):
        self.tool_call_info = tool_call_info
        self.agent_state = agent_state
        self.parent_span = parent_span
        self.tracer = tracer
        self.framework_adapter = framework_adapter

        self.span: Optional[Span] = None
        self.start_time_ns: Optional[int] = None

    def __enter__(self) -> "ToolCallSpan":
        # Prepare parent context from root span (if any)
        root_span = self.parent_span
        parent_span_context = (
            trace.set_span_in_context(root_span) if root_span else None
        )
        self.start_time_ns = time.perf_counter_ns()

        # Start span with placeholder attributes so samplers can access the keys
        self.span = self.tracer.start_span(
            "process_tool_call",
            context=parent_span_context,
            attributes={
                "tool_name": self.tool_call_info.name,
                "tool_args": self.framework_adapter.serialize_tool_args(
                    self.tool_call_info.args
                ),
                "tool_call_id": self.tool_call_info.id,
                "agent_state": self.framework_adapter.serialize_agent_state(
                    self.agent_state
                ),
            },
        )

        use_span(self.span)
        return self

    def save_result(self, process_tool_call_result: ProcessToolCallResultPy) -> None:
        if not self.span:
            return  # todo: Gracefully handle close() being called twice. https://linear.app/friskai/issue/POL-98/gracefully-handle-spans-being-opened-or-closed-twice
        # Set final attributes from the policy engine result
        self.span.set_attributes(
            {
                "decision": process_tool_call_result.decision,
                "matched_rules": process_tool_call_result.rules_matched_count,
            }
        )

        if process_tool_call_result.reason is not None:
            self.span.set_attribute("reason", process_tool_call_result.reason)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If an exception occurs inside the context, end the span gracefully
        if self.span:
            # Record latency even on exception
            end_time = time.perf_counter_ns()
            latency_ns = (
                None if self.start_time_ns is None else end_time - self.start_time_ns
            )
            try:
                self.span.set_attribute("latency_ns", latency_ns)
                if exc_type:
                    # Minimal error tagging
                    self.span.set_attribute("error.type", str(exc_type))
                    if exc_val:
                        self.span.set_attribute("error.message", str(exc_val))
                    else:
                        self.span.set_attribute("error.message", "Unknown error")
            finally:
                self.span.end()
        # Propagate exception (do not suppress)
        return False
