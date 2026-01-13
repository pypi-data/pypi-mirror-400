from typing import Any, Protocol, runtime_checkable


class MetadataGenerator(Protocol):
    """Protocol defining the interface for metadata generation strategies.

    Classes implementing this protocol should provide metadata enrichment
    for individual chunks based on the full document text. Metadata can include
    context, summaries, keywords, embeddings, or any other information that
    enhances chunk understanding in retrieval or analysis tasks.

    Multiple generators can be applied sequentially to enrich chunks with
    different types of metadata. When multiple generators return the same
    metadata key, later generators' values will overwrite earlier ones.

    Important: The generate_metadata method must return a dict. Returning any
    other type will cause a TypeError to be raised by the chunker.

    Example:
        >>> class ContextMetadataGenerator:
        ...     def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        ...         return {"context": f"This chunk is from a document about: {text[:50]}"}

        >>> class KeywordMetadataGenerator:
        ...     def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        ...         keywords = extract_keywords(chunk_text)
        ...         return {"keywords": keywords, "keyword_count": len(keywords)}
    """

    def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        """Generate metadata for a chunk.

        Args:
            text: The full document text.
            chunk_text: The specific chunk text to generate metadata for.

        Returns:
            A dictionary of metadata to add to the chunk. This MUST be a dict;
            returning any other type will raise TypeError. The generator controls
            what keys and values are added. Common keys include:
            - "context": Contextual information about the chunk
            - "summary": A brief summary of the chunk
            - "keywords": List of keywords extracted from the chunk
            - "sentiment": Sentiment analysis results
            - "embedding": Vector embedding of the chunk

            The returned dictionary will be merged into the chunk's metadata using
            dict.update(), so keys from this generator will overwrite any existing
            keys with the same name.
        """
        ...


@runtime_checkable
class AsyncMetadataGenerator(Protocol):
    """Protocol defining the interface for async metadata generation strategies.

    Classes implementing this protocol should provide metadata enrichment
    for individual chunks based on the full document text. Metadata can include
    context, summaries, keywords, embeddings, or any other information that
    enhances chunk understanding in retrieval or analysis tasks.

    This async version allows for parallel metadata generation across multiple
    chunks, providing significant performance improvements when calling I/O-bound
    services like LLM APIs.

    Multiple generators can be applied sequentially to enrich chunks with
    different types of metadata. When multiple generators return the same
    metadata key, later generators' values will overwrite earlier ones.

    Important: The generate_metadata method must return a dict. Returning any
    other type will cause a TypeError to be raised by the chunker.

    All implementing classes must provide:
    1. A name identifier (class variable)
    2. A get_max_concurrency() method that returns the rate limit
    3. A generate_metadata() method that produces metadata

    Example:
        >>> class AsyncContextMetadataGenerator:
        ...     def get_max_concurrency(self) -> int | None:
        ...         return 5  # Limit to 5 concurrent API calls
        ...
        ...     async def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        ...         # Call async LLM API
        ...         context = await llm_client.generate(f"Summarize: {chunk_text}")
        ...         return {"context": context}

        >>> class AsyncKeywordMetadataGenerator:
        ...
        ...     def get_max_concurrency(self) -> int | None:
        ...         return 20  # Local processing, can handle more
        ...
        ...     async def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        ...         keywords = await extract_keywords_async(chunk_text)
        ...         return {"keywords": keywords, "keyword_count": len(keywords)}

        >>> class UnlimitedGenerator:
        ...     def get_max_concurrency(self) -> int | None:
        ...         return None  # No rate limiting
        ...
        ...     async def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        ...         return {"data": await fast_local_operation(chunk_text)}
    """

    def get_max_concurrency(self) -> int | None:
        """Return the maximum number of concurrent metadata generation calls.

        This method is called once when the generator is used to determine rate limiting.
        It allows for both static and dynamic concurrency control.

        Returns:
            An integer to limit concurrent calls (e.g., 5 for rate-limited APIs),
            or None for unlimited concurrency (e.g., fast local operations).

        Example:
            Static limit:
            >>> def get_max_concurrency(self) -> int | None:
            ...     return 5  # Always limit to 5 concurrent calls

            Dynamic limit:
            >>> def get_max_concurrency(self) -> int | None:
            ...     return 5 if is_peak_hours() else 20  # Adjust based on conditions

            Unlimited:
            >>> def get_max_concurrency(self) -> int | None:
            ...     return None  # No rate limiting
        """
        ...

    async def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        """Asynchronously generate metadata for a chunk.

        Args:
            text: The full document text.
            chunk_text: The specific chunk text to generate metadata for.

        Returns:
            A dictionary of metadata to add to the chunk. This MUST be a dict;
            returning any other type will raise TypeError. The generator controls
            what keys and values are added. Common keys include:
            - "context": Contextual information about the chunk
            - "summary": A brief summary of the chunk
            - "keywords": List of keywords extracted from the chunk
            - "sentiment": Sentiment analysis results
            - "embedding": Vector embedding of the chunk

            The returned dictionary will be merged into the chunk's metadata using
            dict.update(), so keys from this generator will overwrite any existing
            keys with the same name.
        """
        ...
