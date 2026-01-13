from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Chunk:
    """Represents a chunk of text with associated metadata.

    A Chunk is the fundamental unit returned by text splitters. It contains
    the text content, token count, and optional metadata such as context,
    headers, or other information about the chunk's origin.

    Attributes:
        text: The text content of the chunk.
        token_count: The number of tokens in the chunk, calculated using
            the configured token counter (default: tiktoken o200k_base).
        metadata: Additional information about the chunk, such as:
            - headers: Markdown headers hierarchy (when using MarkdownSplitter)
            - source: Original file path or identifier
            - context: Contextual information (added by metadata generators)
            - keywords: Extracted keywords (added by metadata generators)
            - summary: Brief summary (added by metadata generators)
            - Any custom metadata added by splitters or metadata generators

    Example:
        >>> chunk = Chunk(
        ...     text="This is a sample chunk.",
        ...     token_count=6,
        ...     metadata={"source": "document.md", "section": "Introduction"}
        ... )
        >>> print(chunk.text)
        This is a sample chunk.
        >>> print(chunk.token_count)
        6
    """

    text: str
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)
