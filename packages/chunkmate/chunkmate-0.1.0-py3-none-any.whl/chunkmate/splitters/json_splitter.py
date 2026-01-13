import json
from collections.abc import Callable
from typing import Any

from langchain_text_splitters import (
    RecursiveJsonSplitter,
)

from chunkmate.chunkers.chunk import Chunk
from chunkmate.splitters.protocols import Splitter
from chunkmate.utils.tokens import default_token_counter


class JSONSplitter(Splitter):
    """A splitter for JSON documents that recursively splits JSON data while preserving structure.

    This splitter converts JSON text into structured chunks that respect JSON boundaries,
    ensuring that each chunk contains valid JSON. It uses a recursive approach to split
    large JSON documents while maintaining the hierarchical structure where possible.

    If the entire JSON document fits within the max_chunk_size, it returns a single chunk.
    Otherwise, it recursively splits the JSON structure into smaller valid JSON chunks.

    Args:
        max_chunk_size: Maximum number of tokens per chunk. Defaults to 512.
        count_tokens: Function to count tokens in a string. Defaults to default_token_counter.

    Attributes:
        max_chunk_size: Maximum number of tokens per chunk.
        count_tokens: Function used to count tokens in text.
        splitter: Underlying RecursiveJsonSplitter from langchain_text_splitters.

    Examples:
        >>> splitter = JSONSplitter(max_chunk_size=100)
        >>> json_text = '{"name": "John", "age": 30, "city": "New York"}'
        >>> chunks = splitter.split(json_text)
        >>> len(chunks)
        1
        >>> chunks[0].text
        '{"name": "John", "age": 30, "city": "New York"}'
    """

    def __init__(
        self,
        max_chunk_size: int = 512,
        count_tokens: Callable[[str], int] = default_token_counter,
    ):
        self.max_chunk_size = max_chunk_size
        self.count_tokens = count_tokens
        self.splitter = RecursiveJsonSplitter(max_chunk_size=max_chunk_size)

    def split(self, text: str) -> list[Chunk]:
        text = text.strip()
        if not text:
            return []

        total_tokens = self.count_tokens(text)
        if total_tokens <= self.max_chunk_size:
            return [
                Chunk(
                    text=text,
                    token_count=total_tokens,
                )
            ]

        json_data: dict[str, Any] = json.loads(text)
        chunks: list[Chunk] = []
        for chunk in self.splitter.split_json(json_data=json_data):
            s = json.dumps(chunk)
            chunks.append(
                Chunk(
                    text=s,
                    token_count=self.count_tokens(s),
                )
            )

        return chunks

    def can_handle(self, text: str) -> bool:
        try:
            _ = json.loads(text.strip())
            return True
        except json.JSONDecodeError:
            return False
