import asyncio
import inspect
from typing import AsyncGenerator, AsyncIterator, Awaitable, Callable, Optional, Union

from langchain_core.messages import ContentBlock, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk

from frisk_sdk._experimental.content_block_utils import (
    is_text_content_block,
    extract_text_from_chunk,
)

TransformReturn = Union[ContentBlock, AsyncGenerator[ContentBlock, None]]
TransformFn = Callable[
    [ContentBlock], Union[TransformReturn, Awaitable[TransformReturn]]
]


async def maybe_await(value):
    if asyncio.iscoroutine(value) or asyncio.isfuture(value):
        return await value
    return value


class StreamTransformer:
    """
    Single-worker async chunk transformer with decoupled emissions.
    No max queue size, no concurrency.
    """

    def __init__(self, transform: TransformFn):
        self._transform = transform
        self._in_q: asyncio.Queue[Optional[AIMessageChunk]] = (
            asyncio.Queue()
        )  # unbounded
        self._out_q: asyncio.Queue[Optional[ChatGenerationChunk]] = (
            asyncio.Queue()
        )  # unbounded
        self._input_worker: Optional[asyncio.Task] = None
        self._closed_in = False
        self._closed_out = False
        self._text_buffer: str = ""

    async def __aenter__(self):
        self._ensure_worker()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    def _ensure_worker(self):
        if self._input_worker is None or self._input_worker.done():
            self._input_worker = asyncio.create_task(self._run())

    """
    while true:
    - Get the next chunk from the input queue
    - If the chunk is None:
        - exit the loop
    - Else, ingest the chunk.
    """

    async def _run(self):
        try:
            while True:
                item = await self._in_q.get()
                if item is None:
                    self._in_q.task_done()
                    await self.process_text_buffer()
                    break
                try:
                    await self.ingest_message_chunk(item)
                finally:
                    self._in_q.task_done()
        finally:
            if not self._closed_out:
                await self._out_q.put(None)
                self._closed_out = True

    async def ingest_message_chunk(self, message_chunk: AIMessageChunk):
        content_blocks = message_chunk.content_blocks
        for content_block in content_blocks:
            await self.ingest_content_block(content_block, message_chunk)

    """
    - If the chunk is a text block:
        - Add it to the pending queue
    - If the chunk is not a text block:
        - Wait for the pending queue to be empty
        - Add the chunk to the output queue
    - Else (if the chunk is a text block):
        - Add the chunk to the pending 
    """

    async def ingest_content_block(
        self, content_block: ContentBlock, message_chunk: AIMessageChunk
    ):
        if is_text_content_block(content_block):
            await self.add_text_to_buffer(content_block)
            # if self.should_process_text_buffer(block):
            #     await self.process_text_buffer()
        else:
            await self.process_text_buffer()
            await self._out_q.put(
                ChatGenerationChunk(
                    message=AIMessageChunk(
                        content_blocks=[content_block],
                        tool_calls=getattr(message_chunk, "tool_calls", None),
                        additional_kwargs=getattr(
                            message_chunk, "additional_kwargs", {}
                        ),
                        id=getattr(message_chunk, "id", None),
                        name=getattr(message_chunk, "name", None),
                        response_metadata=getattr(
                            message_chunk, "response_metadata", None
                        ),
                        usage_metadata=getattr(message_chunk, "usage_metadata", None),
                    )
                )
            )

    async def process_text_buffer(self):
        if len(self._text_buffer) == 0:
            return

        try:
            transform_result = await maybe_await(self._transform(self._text_buffer))
            if inspect.isasyncgen(transform_result):  # async generator -> stream many
                async for transformed_text in transform_result:  # type: ignore[misc]
                    await self.add_text_to_output_queue(transformed_text)
            else:  # single content block
                await self.add_text_to_output_queue(transform_result)  # type: ignore[arg-type]

        except Exception as e:
            # Surface transform errors downstream as a chunk of the same "kind"
            error_text = (
                f"[transform-error]: {e}"
                if isinstance(self._text_buffer, str)
                else f"[transform-error]: {e}".encode()
            )
            await self.add_text_to_output_queue(error_text)  # type: ignore[arg-type]

        finally:
            self._text_buffer = ""

    async def add_text_to_output_queue(self, transformed_text: str):
        return await self._out_q.put(
            ChatGenerationChunk(
                message=AIMessageChunk(
                    content_blocks=[{"type": "text", "text": transformed_text}]
                )
            )
        )

    async def add_text_to_buffer(self, block: ContentBlock):
        self._text_buffer += extract_text_from_chunk(block)
        if "id" in block and block["text"] == "":
            await self._out_q.put(
                ChatGenerationChunk(
                    message=AIMessageChunk(
                        content_blocks=[{"id": block["id"], "type": "text", "text": ""}]
                    )
                )
            )
            await self.process_text_buffer()

    async def feed(self, chunk: AIMessageChunk):
        if self._closed_in:
            raise RuntimeError("Cannot feed after end()")
        self._ensure_worker()
        await self._in_q.put(chunk)

    async def end(self):
        if self._closed_in:
            return
        self._closed_in = True
        self._ensure_worker()
        await self._in_q.put(None)

    async def aclose(self):
        await self.end()
        if self._input_worker:
            await self._input_worker

    def __aiter__(self) -> AsyncIterator[ContentBlock]:
        self._ensure_worker()
        return self._iterate_outputs()

    async def _iterate_outputs(self) -> AsyncIterator[ChatGenerationChunk]:
        while True:
            chunk = await self._out_q.get()
            if chunk is None:
                self._out_q.task_done()
                break
            try:
                yield chunk
            finally:
                self._out_q.task_done()
