"""Chunkmate - A text chunking library for processing documents."""

import logging

from chunkmate.chunkers import AsyncChunker, Chunk, Chunker
from chunkmate.metadata import AsyncMetadataGenerator, MetadataGenerator
from chunkmate.splitters import (
    HTMLSplitter,
    JSONSplitter,
    MarkdownSplitter,
    Splitter,
    TextSplitter,
)
from chunkmate.utils.converters import ChunkDict, chunks_to_dict, chunks_to_langchain, chunks_to_llamaindex

__all__ = [
    # Chunk(er)s
    "Chunk",
    "Chunker",
    "AsyncChunker",
    # Generators
    "MetadataGenerator",
    "AsyncMetadataGenerator",
    # Splitters
    "Splitter",
    "HTMLSplitter",
    "JSONSplitter",
    "MarkdownSplitter",
    "TextSplitter",
    # Utils
    "ChunkDict",
    "chunks_to_langchain",
    "chunks_to_llamaindex",
    "chunks_to_dict",
]

# Add NullHandler to prevent "No handlers found" warnings when library is used
# Applications using this library should configure their own logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
