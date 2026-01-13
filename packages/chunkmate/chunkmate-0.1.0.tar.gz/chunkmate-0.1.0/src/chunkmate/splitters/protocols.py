from typing import Protocol

from chunkmate.chunkers.chunk import Chunk


class Splitter(Protocol):
    """Protocol defining the interface for text splitting strategies.

    Splitter is the base protocol that all text splitters must implement.
    It provides a unified interface for breaking down text documents into
    smaller, manageable chunks based on different strategies (e.g., by
    headers, paragraphs, tokens, or custom logic).

    Implementations of this protocol can use various strategies such as:
    - Header-based splitting (e.g., MarkdownSplitter)
    - Recursive character splitting (e.g., TextSplitter)
    - Semantic splitting based on meaning
    - Fixed-size token-based splitting
    - Custom domain-specific splitting logic

    The protocol ensures that all splitters can be used interchangeably
    within the Chunker class, allowing for flexible document processing.

    Example:
        Implementing a custom splitter:
        >>> class SentenceSplitter:
        ...     def split(self, text: str) -> list[Chunk]:
        ...         sentences = text.split('. ')
        ...         return [Chunk(text=s, token_count=len(s.split()))
        ...                 for s in sentences]
        >>>
        >>> splitter = SentenceSplitter()
        >>> chunks = splitter.split("First sentence. Second sentence.")
    """

    def split(self, text: str) -> list[Chunk]:
        """Split text into a list of chunks.

        This method takes a text string and breaks it down into multiple
        Chunk objects according to the specific splitting strategy implemented
        by the class.

        Args:
            text: The text content to be split into chunks. The format and
                  structure of the text may be interpreted differently by
                  different splitter implementations.

        Returns:
            A list of Chunk objects. Each Chunk should contain:
            - text: The chunk's text content
            - token_count: The number of tokens in the chunk
            - metadata: Optional metadata dict (can be empty)

            An empty list should be returned if the input text is empty or
            if no valid chunks can be created.

        Example:
            >>> splitter = TextSplitter(max_chunk_size=100)
            >>> chunks = splitter.split("Some long text content here...")
            >>> for chunk in chunks:
            ...     print(f"Chunk has {chunk.token_count} tokens")
        """
        ...

    def can_handle(self, text: str) -> bool:
        """Determine if this splitter can handle the given text.

        This method analyzes the text content to determine if this splitter
        is appropriate for processing it. Each splitter implementation should
        define its own logic for detecting compatible text formats.

        Implementations can use various detection strategies:
        - Pattern matching (e.g., regex for Markdown headers)
        - Scoring systems (e.g., counting multiple format indicators)
        - Always accepting (e.g., TextSplitter as a universal fallback)
        - File signatures or magic numbers
        - Language detection

        This method is typically used by the Chunker class to automatically
        select the most appropriate splitter for a given text, enabling
        intelligent format detection without explicit user specification.

        Args:
            text: The text content to analyze for format detection.

        Returns:
            True if this splitter can handle the text format, False otherwise.

        Note:
            When multiple splitters return True, the Chunker typically uses
            the first match. Therefore, more specialized splitters should be
            registered before general-purpose ones to ensure proper precedence.

        Example:
            >>> class MarkdownSplitter:
            ...     def can_handle(self, text: str) -> bool:
            ...         return text.startswith('#') or '##' in text
            ...
            >>> class TextSplitter:
            ...     def can_handle(self, text: str) -> bool:
            ...         return True  # Accepts anything as fallback
            ...
            >>> md_splitter = MarkdownSplitter()
            >>> md_splitter.can_handle("## Header\n\nContent")
            True
            >>> md_splitter.can_handle("Plain text")
            False
        """
        ...
