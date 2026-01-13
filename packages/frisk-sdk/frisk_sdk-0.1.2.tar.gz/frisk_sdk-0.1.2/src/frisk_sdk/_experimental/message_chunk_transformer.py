from __future__ import annotations

import asyncio
from typing import Callable, Optional, AsyncGenerator, List

from langchain_core.messages import AIMessageChunk, ContentBlock
from langchain_core.outputs import ChatGenerationChunk

from .content_block_utils import is_text_content_block
from frisk_sdk._experimental.message_transformer import Chunk, MessageTransformer


class MessageChunkTransformer:
    def __init__(self, rewrite_text_fn: Callable[[str], str]):
        self._rewrite_text = rewrite_text_fn
        self._input_queue: asyncio.Queue[Optional[Chunk]] = asyncio.Queue()  # unbounded
        self._output_queue: asyncio.Queue[Optional[Chunk]] = (
            asyncio.Queue()
        )  # unbounded

    async def process_chunk(
        self, chunk: AIMessageChunk
    ) -> AsyncGenerator[ChatGenerationChunk, None]:
        input_content_blocks = chunk.content_blocks
        async for transformed_content_blocks in self.process_blocks(
            input_content_blocks
        ):
            yield ChatGenerationChunk(AIMessageChunk(transformed_content_blocks))

    async def process_blocks(
        self, blocks: List[ContentBlock]
    ) -> AsyncGenerator[List[ContentBlock], None]:
        i = 0
        n = len(blocks)
        while i < n:
            first = blocks[i]
            if is_text_content_block(first):
                transformer = MessageTransformer(self._rewrite_text)
                while i < n and is_text_content_block(blocks[i]):
                    await transformer.feed(self.extract_text_from_chunk(blocks[i]))
                    i += 1
                await transformer.end()
                async for out in transformer:
                    yield [{"type": "text", "text": out}]
            else:
                non_string_blocks: List[ContentBlock] = []
                while i < n and not isinstance(blocks[i], str):
                    non_string_blocks.append(blocks[i])
                    i += 1
                yield non_string_blocks
