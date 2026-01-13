from __future__ import annotations

from typing import Callable, Any, Iterator, AsyncIterator, Sequence, Optional

from pydantic import PrivateAttr
from pydantic import ConfigDict  # pydantic v2
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk
from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
from langchain_core.runnables import RunnableConfig

from .drop_token_events_callback_handler import (
    DropTokenEvents,
)
from frisk_sdk._experimental.stream_transformer import StreamTransformer

RewriteFn = Callable[[str], str]


class RewritingChatModel(BaseChatModel):
    # allow Callable + foreign model types as fields
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _wrapped_model: BaseChatModel = PrivateAttr()
    _rewrite_text: Callable[[str], str] = PrivateAttr()

    def __init__(
        self,
        wrapped_model: BaseChatModel,
        rewrite_text_fn: Callable[[str], str],
        **data,
    ):
        super().__init__(**data)
        # HARD RESET any bound handlers on the inner model
        self._rewrite_text = rewrite_text_fn
        self._wrapped_model = wrapped_model  # <-- note the leading underscore

    @property
    def _llm_type(self) -> str:
        return f"rewriter[{getattr(self._wrapped_model, '_llm_type', type(self._wrapped_model).__name__)}]"

    # todo: Implement _identifying_params and other Langchain builtins.
    # https: // linear.app / friskai / issue / SDK - 24 / fix - issues - in -llm - output - middleware
    # def _identifying_params(self) -> dict:
    #     get = getattr(self._wrapped_model, "_identifying_params", lambda: {})
    #     return {"inner": get()}

    # ----- non-stream path
    def _generate(self, messages: Sequence[BaseMessage], **kwargs: Any) -> ChatResult:
        base_msg: AIMessage = self._wrapped_model.invoke(messages, **kwargs)
        out = self._rewrite_message(base_msg)
        return ChatResult(generations=[ChatGeneration(message=out)])

    def bind_tools(self, *args, **kwargs):
        bound_wrapped_model = self._wrapped_model.bind_tools(*args, **kwargs)
        self._wrapped_model = bound_wrapped_model
        return self

    # ----- stream path (sync)
    def _stream(
        self,
        messages: Sequence[BaseMessage],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        outer_callbacks = list(
            (config.callbacks if config and hasattr(config, "callbacks") else [])
        )
        inner_config = config
        if inner_config is not None:
            inner_config = inner_config.copy()
            inner_config.callbacks = [
                DropTokenEvents(callback_handler)
                for callback_handler in outer_callbacks
            ]
        for chunk in self._wrapped_model.stream(
            messages, config=inner_config, **kwargs
        ):
            yield ChatGenerationChunk(message=self._rewrite_chunk(chunk))

    # ----- stream path (async)
    async def _astream(
        self,
        messages: Sequence[BaseMessage],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        outer_callbacks = list(
            (config["callbacks"] if config and hasattr(config, "callbacks") else [])
        )
        inner_config = config.copy() if config else RunnableConfig()
        if inner_config is not None:
            inner_config = inner_config.copy()

        inner_config["callbacks"] = [
            DropTokenEvents(callback_handler) for callback_handler in outer_callbacks
        ]

        stream_transformer = StreamTransformer(self._rewrite_text)

        async def feed_chunks():
            response = self._wrapped_model.astream(
                messages, config=inner_config, **kwargs
            )
            async for chunk in response:
                await stream_transformer.feed(chunk)
            await stream_transformer.end()
            return

        await feed_chunks()

        # todo: Properly bubble up errors when feed_chunks() is called as a separate asyncio task.
        # feed_task = asyncio.create_task(feed_chunks())
        async for out in stream_transformer:
            yield out
        # await feed_task
        return

    # ----- helpers
    def _rewrite_chunk(self, chunk: AIMessageChunk) -> AIMessageChunk:
        content = chunk.content
        chunk_text = chunk.text()
        if isinstance(chunk_text, str):
            content = self._rewrite_text(chunk_text)
        elif isinstance(chunk.content, list):
            content = [
                self._rewrite_text(p.text()) if hasattr(p, "text") and p.text() else p
                for p in chunk.content
            ]
        return AIMessageChunk(content)

    def _rewrite_message(self, msg: AIMessage) -> AIMessage:
        c = msg.content
        if isinstance(c, str):
            c = self._rewrite_text(c)
        elif isinstance(c, list):
            c = [self._rewrite_text(p) if isinstance(p, str) else p for p in c]
        return AIMessage(
            content=c,
            additional_kwargs=getattr(msg, "additional_kwargs", {}),
            tool_calls=getattr(msg, "tool_calls", None),
            tool_call_chunks=getattr(msg, "tool_call_chunks", None),
            lc_attributes=getattr(msg, "lc_attributes", None),
            lc_secrets=getattr(msg, "lc_secrets", None),
            id=getattr(msg, "id", None),
            name=getattr(msg, "name", None),
            response_metadata=getattr(msg, "response_metadata", None),
            usage_metadata=getattr(msg, "usage_metadata", None),
        )


# Example rewrite function
def redact_numbers(text: str) -> str:
    return "".join("#" if ch.isdigit() else ch for ch in text)
