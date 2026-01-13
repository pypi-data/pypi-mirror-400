import re
from collections.abc import Callable
from typing import ClassVar

from html2text import html2text
from langchain_text_splitters import MarkdownHeaderTextSplitter

from chunkmate.chunkers.chunk import Chunk
from chunkmate.splitters.protocols import Splitter
from chunkmate.utils.tokens import default_token_counter


class HTMLSplitter(Splitter):
    """A text splitter designed to handle HTML content.

    This splitter converts HTML content to Markdown format and then splits it
    based on header hierarchy. It uses html2text for conversion and the
    MarkdownHeaderTextSplitter for intelligent splitting along document structure.

    The splitter can automatically detect HTML content through pattern matching
    of common HTML elements and attributes. It's particularly useful for processing
    web pages, HTML documentation, and other HTML-formatted content while preserving
    semantic structure.

    Attributes:
        max_chunk_size: Maximum size in tokens for each chunk. Default is 512.
        count_tokens: Callable function to count tokens in text. Uses default_token_counter if not specified.
        splitter: Internal MarkdownHeaderTextSplitter instance used for splitting converted Markdown.
        HTML_INDICATORS: Class variable containing regex patterns for detecting HTML content.

    Example:
        >>> splitter = HTMLSplitter(max_chunk_size=1024)
        >>> html_content = "<html><body><h2>Title</h2><p>Content here</p></body></html>"
        >>> chunks = splitter.split(html_content)
        >>> for chunk in chunks:
        ...     print(f"Chunk: {chunk.text[:50]}... ({chunk.token_count} tokens)")
    """

    _HTML_INDICATORS: ClassVar[list[str]] = [
        r"<html[>\s]",  # HTML document tag
        r"<head[>\s]",  # Head tag
        r"<body[>\s]",  # Body tag
        r"<!DOCTYPE\s+html",  # HTML5 doctype
        r"<div[>\s]",  # Div tag
        r"<p[>\s]",  # Paragraph tag
        r"<span[>\s]",  # Span tag
        r"<a\s+[^>]*href",  # Anchor tag with href
        r"<h[1-6][>\s]",  # Header tags h1-h6
        r"<ul[>\s]|<ol[>\s]|<li[>\s]",  # List tags
        r"<table[>\s]|<tr[>\s]|<td[>\s]",  # Table tags
        r"<img\s+[^>]*src",  # Image tag with src
        r"<br\s*/?>|<hr\s*/?>",  # Self-closing tags
        r"<script[>\s]|<style[>\s]",  # Script or style tags
        r"\s(class|id)\s*=\s*[\"']",  # Common attributes
    ]

    def __init__(
        self,
        max_chunk_size: int = 512,
        count_tokens: Callable[[str], int] = default_token_counter,
    ):
        """Initialize the HTMLSplitter.

        Args:
            max_chunk_size: Maximum number of tokens per chunk. Chunks will be split
                at header boundaries when content exceeds this size. Default is 512.
            count_tokens: Function to count tokens in a text string. Should take a
                string as input and return an integer token count. Defaults to
                default_token_counter.

        Note:
            The splitter targets H2 (##) and H3 (###) headers in the converted
            Markdown for splitting boundaries. Headers are preserved in the output.
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
        """Split HTML text into chunks based on header structure.

        This method performs the following steps:
        1. Strips whitespace from the input text
        2. Converts HTML to Markdown using html2text
        3. If content fits within max_chunk_size, returns a single chunk
        4. Otherwise, splits along H2 and H3 header boundaries

        Args:
            text: The HTML text content to split into chunks.

        Returns:
            A list of Chunk objects, each containing:
                - text: The chunk's text content (in Markdown format)
                - token_count: The number of tokens in the chunk

            Returns an empty list if the input text is empty or whitespace-only.

        Note:
            The conversion from HTML to Markdown helps preserve document structure
            while making the content more suitable for language models and text
            processing. Headers are used as natural splitting points to maintain
            semantic coherence within chunks.

        Example:
            >>> splitter = HTMLSplitter(max_chunk_size=100)
            >>> html = "<h2>Section 1</h2><p>Content 1</p><h2>Section 2</h2><p>Content 2</p>"
            >>> chunks = splitter.split(html)
            >>> len(chunks)
            2
        """
        text = text.strip()
        if not text:
            return []

        text = html2text(text).strip()
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

        Analyzes the text content to detect if it contains HTML formatting
        by searching for common HTML patterns. Uses a scoring system that
        requires multiple different HTML indicators to be present to avoid
        false positives from plain text that might contain angle brackets.

        The method checks for these HTML indicators:
        - HTML tags (opening and closing)
        - Common HTML elements (div, p, span, a, etc.)
        - HTML document structure (html, head, body)
        - Self-closing tags (br, hr, img, etc.)
        - HTML attributes (class, id, href, src, etc.)

        Args:
            text: The text content to analyze for HTML patterns.

        Returns:
            True if 3 or more HTML patterns are found, indicating this is
            likely an HTML document. False otherwise.

        Note:
            The scoring system with a threshold of 3+ indicators helps avoid
            false positives. Real HTML documents typically contain multiple
            HTML features (e.g., tags, attributes, and document structure),
            while plain text or Markdown with occasional HTML tags might only
            match 1-2 patterns.

        Example:
            >>> splitter = HTMLSplitter()
            >>> html_text = "<html><body><h1>Title</h1><p>Content</p></body></html>"
            >>> splitter.can_handle(html_text)
            True
            >>> plain_text = "Just some plain text content"
            >>> splitter.can_handle(plain_text)
            False
        """
        text = text.strip()
        if not text:
            return False

        score = 0
        for pattern in self._HTML_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1

        return score >= 3
