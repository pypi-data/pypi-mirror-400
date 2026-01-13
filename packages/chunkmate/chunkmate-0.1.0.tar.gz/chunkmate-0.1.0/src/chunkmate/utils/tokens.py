"""Token counting utilities for text chunking.

This module provides token counting functions used by splitters to determine
chunk sizes. The default implementation uses OpenAI's tiktoken library with
the o200k_base encoding, which is compatible with the latest GPT-4o models.

Encoding Compatibility:
- o200k_base (default): GPT-4o, GPT-4o-mini, ChatGPT-4o-latest
- cl100k_base: GPT-4, GPT-4-turbo, GPT-3.5-turbo, text-embedding-3-*
- p50k_base: GPT-3 models (Davinci, Curie, Babbage, Ada)

For older models, provide a custom token counter with the appropriate encoding.
"""

import tiktoken

from chunkmate.chunkers.chunk import Chunk

encoding = tiktoken.get_encoding(encoding_name="o200k_base")


def default_token_counter(text: str) -> int:
    """Count tokens in text using OpenAI's o200k_base encoding.

    This is the default token counter used by all splitters in chunkmate.
    It uses tiktoken's o200k_base encoding, which is the encoding used by
    OpenAI's latest GPT-4o and GPT-4o-mini models. This ensures that token
    counts are accurate when chunks are used with these models.

    The o200k_base encoding is more efficient than previous encodings and
    typically produces fewer tokens for the same text. It's based on BPE
    (Byte Pair Encoding) and provides consistent token counting across
    different types of content.

    For compatibility with older models (GPT-4, GPT-3.5-turbo), create a
    custom token counter using cl100k_base encoding.

    Args:
        text: The text string to count tokens for. Can be of any length.

    Returns:
        The number of tokens in the text according to o200k_base encoding.

    Example:
        >>> from chunkmate.utils.tokens import default_token_counter
        >>> text = "Hello, world!"
        >>> token_count = default_token_counter(text)
        >>> print(f"Token count: {token_count}")
        Token count: 4

        Custom token counter for older models (GPT-4, GPT-3.5-turbo):
        >>> import tiktoken
        >>> from chunkmate.splitters.text import TextSplitter
        >>> def cl100k_counter(text: str) -> int:
        ...     encoding = tiktoken.get_encoding("cl100k_base")
        ...     return len(encoding.encode(text))
        >>> splitter = TextSplitter(count_tokens=cl100k_counter)

        Simple word-based counter:
        >>> def word_counter(text: str) -> int:
        ...     return len(text.split())
        >>> splitter = TextSplitter(count_tokens=word_counter)
    """
    return len(encoding.encode(text))


def total_tokens(chunks: list[Chunk]) -> int:
    """Calculate the total number of tokens across all chunks.

    This utility function sums up the token_count attribute from a list of
    Chunk objects, providing a quick way to determine the total token usage
    for a collection of chunks. This is useful for:
    - Validating that chunking stays within token limits
    - Calculating API costs based on total tokens
    - Monitoring token usage in events and logging
    - Comparing different chunking strategies

    Args:
        chunks: A list of Chunk objects to sum tokens for.

    Returns:
        The total number of tokens across all chunks. Returns 0 for an empty list.

    Example:
        >>> from chunkmate.chunkers import Chunker
        >>> from chunkmate.utils.tokens import total_tokens
        >>> chunker = Chunker()
        >>> chunks = chunker.split("# Title\\n\\nSome content here.")
        >>> total = total_tokens(chunks)
        >>> print(f"Total tokens: {total}")
        Total tokens: 8

        Useful for validation:
        >>> max_tokens = 1000
        >>> if total_tokens(chunks) > max_tokens:
        ...     print("Warning: chunks exceed token limit!")
    """
    return sum(chunk.token_count for chunk in chunks)
