import re
from collections.abc import Callable
from typing import ClassVar

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
)

from chunkmate.chunkers.chunk import Chunk
from chunkmate.splitters.protocols import Splitter
from chunkmate.utils.tokens import default_token_counter


class MarkdownSplitter(Splitter):
    """A splitter specialized for Markdown documents with header-based splitting.

    MarkdownSplitter intelligently splits Markdown documents by respecting the
    document structure defined by headers (##, ###). It ensures that content
    remains grouped under its relevant headers while respecting token limits.

    The splitter has two modes of operation:
    1. If the entire document fits within max_chunk_size, return it as a single chunk
    2. Otherwise, split by headers (## and ###) using LangChain's MarkdownHeaderTextSplitter

    Attributes:
        max_chunk_size: Maximum number of tokens allowed per chunk.
        count_tokens: Function to count tokens in a text string.
        splitter: The underlying MarkdownHeaderTextSplitter instance.

    Example:
        Basic usage with defaults:
        >>> splitter = MarkdownSplitter()
        >>> text = "## Section 1\\n\\nContent here\\n\\n### Subsection\\n\\nMore content"
        >>> chunks = splitter.split(text)
        >>> for chunk in chunks:
        ...     print(f"Tokens: {chunk.token_count}, Text: {chunk.text[:50]}")

        Custom configuration:
        >>> def custom_counter(text: str) -> int:
        ...     return len(text.split())
        >>> splitter = MarkdownSplitter(max_chunk_size=1024, count_tokens=custom_counter)
        >>> chunks = splitter.split(markdown_text)
    """

    _MARKDOWN_INDICATORS: ClassVar[list[str]] = [
        r"^#{1,6}\s",  # Headers (most distinctive)
        r"^```",  # Code blocks
        r"\[.+\]\(.+\)",  # Links (inline elements)
        r"\*\*.*\*\*",  # Bold text (inline elements)
        r"^[-*+]\s+\S",  # Unordered lists
        r"^\d+\.\s+\S",  # Ordered lists
    ]

    def __init__(
        self,
        max_chunk_size: int = 512,
        count_tokens: Callable[[str], int] = default_token_counter,
    ):
        """Initialize the MarkdownSplitter with token limits and counting function.

        Args:
            max_chunk_size: Maximum number of tokens allowed per chunk. If the entire
                           document is smaller than this, it will be returned as a
                           single chunk. Defaults to 512 tokens.
            count_tokens: A callable that takes a string and returns the token count.
                         Defaults to the default_token_counter which uses tiktoken's
                         o200k_base encoding (used by GPT-4o and GPT-4o-mini).

        Example:
            >>> splitter = MarkdownSplitter(max_chunk_size=1024)
            >>> # or with custom token counter
            >>> splitter = MarkdownSplitter(
            ...     max_chunk_size=256,
            ...     count_tokens=lambda text: len(text) // 4
            ... )
        """
        self.max_chunk_size = max_chunk_size
        self.count_tokens = count_tokens
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
            strip_headers=False,
        )

    def split(self, text: str) -> list[Chunk]:
        """Split Markdown text into chunks based on headers and token limits.

        The splitting strategy is adaptive:
        1. Empty text returns an empty list
        2. If total tokens <= max_chunk_size, returns the entire text as one chunk
        3. Otherwise, splits by Markdown headers (## and ###), preserving structure

        Headers are not stripped from the chunks, allowing readers to understand
        the context and hierarchy of each chunk.

        Args:
            text: The Markdown text to split. Will be stripped of leading/trailing whitespace.

        Returns:
            A list of Chunk objects, each containing:
            - text: The chunk content (including headers)
            - token_count: The number of tokens in the chunk
            - metadata: Empty dict (no metadata added at this level)

        Example:
            >>> splitter = MarkdownSplitter(max_chunk_size=100)
            >>> markdown = '''
            ... ## Introduction
            ... This is the intro section.
            ...
            ... ### Background
            ... Some background information here.
            ...
            ... ## Methods
            ... Description of methods used.
            ... '''
            >>> chunks = splitter.split(markdown)
            >>> print(f"Created {len(chunks)} chunks")
            >>> print(f"First chunk: {chunks[0].text}")
        """
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

        chunks: list[Chunk] = []
        for chunk in self.splitter.split_text(text):
            chunks.append(
                Chunk(
                    text=chunk.page_content,
                    token_count=self.count_tokens(chunk.page_content),
                )
            )

        return chunks

    def can_handle(self, text: str) -> bool:
        """Determine if this splitter can handle the given text.

        Analyzes the text content to detect if it contains Markdown formatting
        by searching for common Markdown patterns. Uses a scoring system that
        requires multiple different Markdown indicators to be present to avoid
        false positives from plain text.

        The method checks for these Markdown indicators:
        - Headers (# ## ### etc.)
        - Code blocks (```)
        - Links ([text](url))
        - Bold text (**text**)
        - Unordered lists (- * +)
        - Ordered lists (1. 2. 3.)

        Args:
            text: The text content to analyze for Markdown patterns.

        Returns:
            True if 2 or more different Markdown patterns are found, indicating
            this is likely a Markdown document. False otherwise.

        Note:
            The threshold of 2+ patterns helps avoid false positives. Real Markdown
            documents typically contain multiple formatting features (e.g., headers
            and lists, or headers and code blocks), while plain text might
            accidentally match a single pattern.

        Example:
            >>> splitter = MarkdownSplitter()
            >>> markdown_text = "## Title\\n\\nSome content\\n\\n- List item"
            >>> splitter.can_handle(markdown_text)
            True
            >>> plain_text = "Just some plain text content"
            >>> splitter.can_handle(plain_text)
            False
        """
        score = 0
        for pattern in self._MARKDOWN_INDICATORS:
            if re.search(pattern, text, re.MULTILINE):
                score += 1

        return score >= 2
