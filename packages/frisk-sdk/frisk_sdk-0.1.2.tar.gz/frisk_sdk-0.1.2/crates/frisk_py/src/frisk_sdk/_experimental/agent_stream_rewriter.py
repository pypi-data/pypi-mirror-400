from __future__ import annotations

from typing import (
    Any,
    AsyncIterator,
    Iterator,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from langchain_core.messages import (
    BaseMessage,
    BaseMessageChunk,
    AIMessage,
    AIMessageChunk,
    ToolMessage,
)

from .content_block_utils import is_text_content_block

# Type of your rewrite function: takes text -> returns text
RewriteFn = Callable[[str], str]


# ---------- generic rewriters (strings, messages, nested dicts/lists) ----------


def _rewrite_text(s: str, rewrite_text_fn: RewriteFn) -> str:
    return rewrite_text_fn(s)


def _rewrite_content(content: Any, rewrite_text_fn: RewriteFn) -> Any:
    if is_text_content_block(content):
        return _rewrite_text(content, rewrite_text_fn)
    if isinstance(content, list):
        out: List[Any] = []
        for p in content:
            out.append(_rewrite_text(p, rewrite_text_fn) if isinstance(p, str) else p)
        return out
    return content


def _rewrite_message_like(msg: Union[BaseMessage, BaseMessageChunk], f: RewriteFn):
    # Works for both Message and MessageChunk (Pydantic v2 .copy)
    return msg.model_copy(update={"content": _rewrite_content(msg.content, f)})


def _walk_and_rewrite(obj: Any, f: RewriteFn) -> Any:
    """Best-effort traversal for 'updates'/'custom' payloads."""
    if isinstance(
        obj, (AIMessage, ToolMessage, BaseMessage, AIMessageChunk, BaseMessageChunk)
    ):
        return _rewrite_message_like(obj, f)
    if isinstance(obj, dict):
        return {k: _walk_and_rewrite(v, f) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk_and_rewrite(v, f) for v in obj]
    if isinstance(obj, str):
        return _rewrite_text(obj, f)
    return obj


# ---------- the agent wrapper ----------


class AgentStreamRewriter:
    """
    Wraps an agent (Runnable/graph) and rewrites ALL streamed output:
      - stream_mode="messages": token chunks + final messages
      - stream_mode="updates": state/tool deltas
      - stream_mode="custom": arbitrary tool emissions via get_stream_writer()

    Args:
        agent: The underlying agent/graph/runnable providing .stream/.astream/.invoke/.ainvoke
        rewrite_fn: Callable[str -> str] to rewrite text
    """

    def __init__(self, agent: Any, rewrite_fn: RewriteFn):
        self.agent = agent
        self.rewrite_fn = rewrite_fn

    # ---------- async streaming ----------
    async def astream(
        self,
        *args,
        **kwargs,
    ) -> AsyncIterator[Tuple[Any, str, Any]]:
        async for subgraph, mode, chunk in self.agent.astream(*args, **kwargs):
            yield subgraph, mode, self._rewrite_event(mode, chunk)
        yield None, "messages", (AIMessageChunk(" (Powered by FriskAI)"), {})

    # ---------- sync streaming ----------
    def stream(self, *args, **kwargs) -> Iterator[Tuple[Any, str, Any]]:
        for subgraph, mode, chunk in self.agent.stream(*args, **kwargs):
            yield subgraph, mode, self._rewrite_event(mode, chunk)

    # ---------- non-stream (final result only) ----------
    async def ainvoke(
        self, inputs: Any, *, config: Optional[Dict[str, Any]] = None
    ) -> Any:
        out = await self.agent.ainvoke(inputs, config=config)
        return _walk_and_rewrite(out, self.rewrite_fn)

    def invoke(self, inputs: Any, *, config: Optional[Dict[str, Any]] = None) -> Any:
        out = self.agent.invoke(inputs, config=config)
        return _walk_and_rewrite(out, self.rewrite_fn)

    # ---------- helper ----------
    def _rewrite_event(self, mode: str, payload: Any) -> Any:
        # messages: AIMessageChunk/AIMessage (or containers holding them)
        if mode == "messages":
            if isinstance(payload[0], BaseMessage):
                return (_rewrite_message_like(payload[0], self.rewrite_fn),) + tuple(
                    payload[1:]
                )
            # sometimes it's a dict with 'messages' or 'event' fields
            return _walk_and_rewrite(payload, self.rewrite_fn)

        # updates/custom: arbitrary dicts/lists/messages
        if mode in ("updates", "custom"):
            return _walk_and_rewrite(payload, self.rewrite_fn)

        # unknown mode: pass through unchanged
        return payload
