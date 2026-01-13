from collections.abc import Callable

from langchain_text_splitters import RecursiveCharacterTextSplitter

from chunkmate.chunkers.chunk import Chunk
from chunkmate.splitters.protocols import Splitter
from chunkmate.utils.tokens import default_token_counter


class TextSplitter(Splitter):
    """A general-purpose text splitter using recursive character-based splitting.

    TextSplitter handles plain text documents by recursively trying different
    separators to split the text into manageable chunks. It attempts to preserve
    natural text boundaries by prioritizing paragraph breaks, then line breaks,
    then sentences, and finally individual characters.

    The splitter uses a hierarchical approach with the following separator priority:
    1. Double newlines (paragraphs)
    2. Single newlines (lines)
    3. Spaces (words)
    4. Periods (sentences)
    5. Commas (clauses)
    6. Empty string (individual characters)

    Like MarkdownSplitter, it has two modes:
    1. If the entire text fits within max_chunk_size, return it as a single chunk
    2. Otherwise, recursively split using the separator hierarchy

    Attributes:
        max_chunk_size: Maximum number of tokens allowed per chunk.
        count_tokens: Function to count tokens in a text string.
        splitter: The underlying RecursiveCharacterTextSplitter instance.

    Example:
        Basic usage with defaults:
        >>> splitter = TextSplitter()
        >>> text = "First paragraph.\\n\\nSecond paragraph.\\n\\nThird paragraph."
        >>> chunks = splitter.split(text)
        >>> for chunk in chunks:
        ...     print(f"Tokens: {chunk.token_count}")

        Custom configuration:
        >>> splitter = TextSplitter(max_chunk_size=256)
        >>> chunks = splitter.split(long_text)
    """

    def __init__(
        self,
        max_chunk_size: int = 512,
        count_tokens: Callable[[str], int] = default_token_counter,
    ):
        """Initialize the TextSplitter with token limits and counting function.

        Args:
            max_chunk_size: Maximum number of tokens allowed per chunk. If the entire
                           text is smaller than this, it will be returned as a
                           single chunk. Defaults to 512 tokens.
            count_tokens: A callable that takes a string and returns the token count.
                         Defaults to the default_token_counter which uses tiktoken's
                         o200k_base encoding (used by GPT-4o and GPT-4o-mini).

        Example:
            >>> splitter = TextSplitter(max_chunk_size=1024)
            >>> # or with custom token counter
            >>> def word_counter(text: str) -> int:
            ...     return len(text.split())
            >>> splitter = TextSplitter(count_tokens=word_counter)
        """
        self.max_chunk_size = max_chunk_size
        self.count_tokens = count_tokens
        self.splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "",
            ],
        )

    def split(self, text: str) -> list[Chunk]:
        """Split plain text into chunks using recursive character-based splitting.

        The splitting strategy is adaptive:
        1. Empty text returns an empty list
        2. If total tokens <= max_chunk_size, returns the entire text as one chunk
        3. Otherwise, recursively splits using separators in priority order:
           paragraphs → lines → spaces → periods → commas → characters

        This recursive approach ensures that chunks respect natural text boundaries
        as much as possible while staying within token limits.

        Args:
            text: The plain text to split. Will be stripped of leading/trailing whitespace.

        Returns:
            A list of Chunk objects, each containing:
            - text: The chunk content
            - token_count: The number of tokens in the chunk
            - metadata: Empty dict (no metadata added at this level)

        Example:
            >>> splitter = TextSplitter(max_chunk_size=100)
            >>> text = '''
            ... First paragraph with some content.
            ... It has multiple sentences.
            ...
            ... Second paragraph here.
            ... Also with multiple sentences.
            ...
            ... Third paragraph with more text.
            ... '''
            >>> chunks = splitter.split(text)
            >>> print(f"Created {len(chunks)} chunks")
            >>> for i, chunk in enumerate(chunks, 1):
            ...     print(f"Chunk {i}: {chunk.token_count} tokens")
        """
        text = text.strip()
        if not text:
            return []

        total_tokens = self.count_tokens(text)
        if total_tokens <= self.max_chunk_size:
            # Text is small, so return it in one chunk
            return [
                Chunk(
                    text=text,
                    token_count=total_tokens,
                )
            ]

        chunks: list[Chunk] = []
        for chunk in self.splitter.split_text(text):
            chunks.append(Chunk(text=chunk, token_count=self.count_tokens(chunk)))

        return chunks

    def can_handle(self, text: str) -> bool:
        """Determine if this splitter can handle the given text.

        TextSplitter is a universal fallback splitter that can handle any plain
        text content. It always returns True because it uses a general-purpose
        recursive character-based splitting strategy that works with any text format.

        This splitter should typically be checked last in a chain of splitters,
        after more specialized splitters (like MarkdownSplitter) have had a chance
        to claim the text if they detect format-specific patterns.

        Args:
            text: The text content to analyze (unused, but kept for protocol consistency).

        Returns:
            Always returns True, as TextSplitter can handle any text content.

        Note:
            While this splitter can technically handle any text, specialized splitters
            may provide better results for formatted content (e.g., Markdown, HTML).
            The Chunker class typically iterates through splitters and uses the first
            one that returns True from can_handle(), so TextSplitter should be
            registered last or used as an explicit fallback.

        Example:
            >>> splitter = TextSplitter()
            >>> splitter.can_handle("Any text content whatsoever")
            True
            >>> splitter.can_handle("## Even Markdown")
            True
            >>> splitter.can_handle("")
            True
        """
        return True
