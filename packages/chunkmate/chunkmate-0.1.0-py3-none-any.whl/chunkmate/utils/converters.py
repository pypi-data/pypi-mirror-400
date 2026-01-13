"""Utility functions for converting Chunk objects to other framework formats.

This module provides converters to transform chunkmate Chunk objects into
document formats used by popular LLM frameworks like LangChain and LlamaIndex.
This enables seamless integration with existing RAG and LLM application pipelines.
"""

from typing import Any, TypedDict

from chunkmate.chunkers import Chunk


class ChunkDict(TypedDict):
    """Dictionary representation of a Chunk object.

    Attributes:
        text: The text content of the chunk.
        token_count: The number of tokens in the chunk.
        metadata: Additional metadata associated with the chunk.
    """

    text: str
    token_count: int
    metadata: dict[str, Any]


def chunks_to_langchain(chunks: list[Chunk]) -> list:
    """Convert chunkmate Chunks to LangChain Documents.

    Transforms a list of Chunk objects into LangChain Document objects,
    preserving both text content and metadata. This is useful for integrating
    chunkmate with LangChain-based RAG systems, vector stores, and retrieval chains.

    Args:
        chunks: A list of Chunk objects to convert. Each chunk should have
                text, token_count, and metadata attributes.

    Returns:
        A list of LangChain Document objects. Each Document contains:
        - page_content: The chunk's text
        - metadata: The chunk's metadata dict (including any context or custom fields)

    Raises:
        ImportError: If langchain-core is not installed. Install with:
                    pip install langchain-core

    Example:
        >>> from chunkmate.chunkers import Chunker
        >>> from chunkmate.utils.converters import chunks_to_langchain
        >>>
        >>> chunker = Chunker()
        >>> chunks = chunker.split("# Title\\n\\nSome content here")
        >>> langchain_docs = chunks_to_langchain(chunks)
        >>>
        >>> # Use with LangChain vector store
        >>> from langchain_community.vectorstores import FAISS
        >>> vectorstore = FAISS.from_documents(langchain_docs, embeddings)
    """
    try:
        from langchain_core.documents import Document
    except ImportError as e:
        raise ImportError(
            "langchain-core is required for this function. Install it with: pip install langchain-core"
        ) from e

    return [Document(page_content=c.text, metadata=c.metadata) for c in chunks]


def chunks_to_llamaindex(chunks: list[Chunk]) -> list:
    """Convert chunkmate Chunks to LlamaIndex Documents.

    Transforms a list of Chunk objects into LlamaIndex Document objects,
    preserving both text content and metadata. This enables integration with
    LlamaIndex-based RAG systems, indexes, and query engines.

    Args:
        chunks: A list of Chunk objects to convert. Each chunk should have
                text, token_count, and metadata attributes.

    Returns:
        A list of LlamaIndex Document objects. Each Document contains:
        - text: The chunk's text content
        - metadata: The chunk's metadata dict (including any context or custom fields)

    Raises:
        ImportError: If llama-index-core is not installed. Install with:
                    pip install llama-index-core

    Example:
        >>> from chunkmate.chunkers import Chunker
        >>> from chunkmate.utils.converters import chunks_to_llamaindex
        >>>
        >>> chunker = Chunker()
        >>> chunks = chunker.split("# Title\\n\\nSome content here")
        >>> llama_docs = chunks_to_llamaindex(chunks)
        >>>
        >>> # Use with LlamaIndex
        >>> from llama_index.core import VectorStoreIndex
        >>> index = VectorStoreIndex.from_documents(llama_docs)
        >>> query_engine = index.as_query_engine()
    """
    try:
        from llama_index.core.schema import Document
    except ImportError as e:
        raise ImportError(
            "llama-index-core is required for this function. Install it with: pip install llama-index-core"
        ) from e

    return [Document(text=c.text, metadata=c.metadata) for c in chunks]


def chunks_to_dict(chunks: list[Chunk]) -> list[ChunkDict]:
    """Convert a list of Chunk objects to a list of dictionaries.

    This is a simple serialization utility that converts Chunk objects into
    plain dictionaries. All fields from the Chunk dataclass are included:
    text, token_count, and metadata.

    Use this function when you need to:
    - Serialize chunks to JSON or other formats that don't support custom objects
    - Store chunks in databases or caches
    - Pass chunks to APIs that expect plain dictionaries
    - Integrate with frameworks that aren't directly supported by other converters

    Args:
        chunks: List of Chunk objects to convert.

    Returns:
        List of dictionaries, each containing 'text', 'token_count', and 'metadata' keys.

    Example:
        >>> chunks = [
        ...     Chunk(text="Hello", token_count=1, metadata={"section": "intro"}),
        ...     Chunk(text="World", token_count=1, metadata={"section": "body"}),
        ... ]
        >>> chunks_to_dict(chunks)
        [
            {'text': 'Hello', 'token_count': 1, 'metadata': {'section': 'intro'}},
            {'text': 'World', 'token_count': 1, 'metadata': {'section': 'body'}}
        ]
    """
    return [
        ChunkDict(
            {
                "text": c.text,
                "token_count": c.token_count,
                "metadata": c.metadata,
            }
        )
        for c in chunks
    ]
