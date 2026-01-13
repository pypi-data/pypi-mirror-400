from __future__ import annotations

from langchain_core.messages import ContentBlock


def is_text_content_block(chunk: ContentBlock):
    return chunk["type"] == "text"


def extract_text_from_chunk(chunk: ContentBlock):
    return chunk["text"]
