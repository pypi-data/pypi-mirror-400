import logging
import time
from pathlib import Path
from typing import Any

from chunkmate.chunkers import BaseChunker, Chunk
from chunkmate.metadata import MetadataGenerator
from chunkmate.splitters import Splitter
from chunkmate.utils.reflection import get_class_name


class Chunker(BaseChunker):
    """A flexible document chunker that splits text and files into manageable chunks.

    The Chunker class provides a unified interface for splitting various document types
    into chunks using appropriate splitters. It supports both text content and file paths,
    automatically selecting the right splitter based on file extensions.

    Key features:
    - Support for multiple metadata generators applied sequentially
    - Automatic splitter selection based on file extensions
    - Built-in error handling with ExceptionGroup
    - Detailed logging for debugging and monitoring

    Attributes:
        _EXTENSIONS_TYPE_MAP: Default mapping of file extensions to splitter types.
        _DEFAULT_SPLITTERS: Default splitter classes for supported document types.

    Example:
        Basic usage with default splitters:
        >>> chunker = Chunker()
        >>> chunks = chunker.split("path/to/document.md")
        >>> for chunk in chunks:
        ...     print(chunk.text)

        Custom splitter configuration:
        >>> custom_splitters = {"markdown": CustomMarkdownSplitter()}
        >>> chunker = Chunker(splitters=custom_splitters)
        >>> chunks = chunker.split("# Hello\\n\\nWorld")

        Custom extension mapping:
        >>> extension_map = {"rst": "text"}
        >>> chunker = Chunker(extension_map=extension_map)
        >>> chunks = chunker.split(Path("document.rst"))

        Custom logging:
        >>> import logging
        >>> logger = logging.getLogger("my_app")
        >>> chunker = Chunker(logger=logger)
        >>> chunks = chunker.split("document.md")
    """

    def __init__(
        self,
        splitters: dict[str, Splitter] | None = None,
        extension_map: dict[str, str] | None = None,
        logger: logging.Logger | None = None,
        metadata_generators: list[MetadataGenerator] | MetadataGenerator | None = None,
    ):
        """Initialize the Chunker with custom splitters and extension mappings.

        Args:
            splitters: Optional dictionary mapping splitter type names to Splitter instances.
                      These will be added to or override the default splitters.
                      Keys should match the splitter type names (e.g., "markdown", "text").
            extension_map: Optional dictionary mapping file extensions to splitter type names.
                          This allows custom file extensions to be associated with existing
                          splitter types. All mapped types must have corresponding splitters.
            logger: Optional logger instance for logging chunking operations.
                   If not provided, uses the default logger for this module.
            metadata_generators: Optional MetadataGenerator instance or list of MetadataGenerator
                                instances for enriching chunks with metadata. Multiple generators
                                will be applied sequentially. Each generator can add multiple
                                metadata fields to each chunk.

        Raises:
            ValueError: If an extension in extension_map maps to a splitter type that
                       doesn't exist in the available splitters.

        Example:
            >>> custom_splitter = CustomMarkdownSplitter()
            >>> chunker = Chunker(
            ...     splitters={"markdown": custom_splitter},
            ...     extension_map={"mdown": "markdown"}
            ... )

            With metadata generation:
            >>> class ContextGenerator:
            ...     name = "context"
            ...     def generate_metadata(self, text: str, chunk_text: str) -> dict:
            ...         return {"context": f"Context for: {chunk_text[:50]}"}
            >>> chunker = Chunker(metadata_generators=ContextGenerator())

            With multiple generators:
            >>> chunker = Chunker(metadata_generators=[
            ...     ContextGenerator(),
            ...     KeywordGenerator(),
            ...     SummaryGenerator()
            ... ])
        """
        super().__init__(splitters=splitters, extension_map=extension_map, logger=logger)
        # Normalize to list
        if metadata_generators is None:
            self.metadata_generators: list[MetadataGenerator] = []
        elif isinstance(metadata_generators, list):
            # Type checker needs help understanding this is a list[MetadataGenerator]
            self.metadata_generators = metadata_generators  # type: ignore[assignment]
        else:
            self.metadata_generators = [metadata_generators]

    def _add_metadata(self, text: str, chunks: list[Chunk]) -> list[Chunk]:
        """Add metadata to chunks using the configured metadata generators.

        This internal method enriches each chunk with metadata by calling all configured
        generators sequentially. Each generator can add multiple fields to the chunk's
        metadata. If no generators are configured, the chunks are returned unchanged.

        The method includes detailed logging to track metadata generation progress and
        performance metrics for each generator and chunk.

        Args:
            text: The full document text that was chunked. This is passed to the
                  generators to provide document-level context. Each generator must
                  return a dict; other types will raise TypeError.
            chunks: The list of chunks to enrich with metadata.

        Returns:
            The same list of chunks with metadata added. Each chunk's metadata will
            contain all fields added by the generators. If multiple generators return
            the same key, later generators' values overwrite earlier ones.

        Raises:
            TypeError: If a metadata generator returns a non-dict value.
            ExceptionGroup: If metadata generation fails for any chunks. The ExceptionGroup
                will contain all individual exceptions that occurred during generation.
                This is raised because metadata generation is considered critical.

        Example:
            >>> class ContextGenerator:
            ...     name = "context"
            ...     def generate_metadata(self, text: str, chunk_text: str) -> dict:
            ...         return {"context": f"Document summary: {text[:50]}"}
            >>> chunker = Chunker(metadata_generators=ContextGenerator())
            >>> chunks = [Chunk(text="sample", token_count=1, metadata={})]
            >>> enriched_chunks = chunker._add_metadata("full document text", chunks)
            >>> print(enriched_chunks[0].metadata["context"])
            Document summary: full document text
        """
        if not self.metadata_generators:
            return chunks

        total_start_time = time.perf_counter()

        for generator in self.metadata_generators:
            self.logger.debug("Starting metadata generation with '%s'", get_class_name(generator))
            generator_start_time = time.perf_counter()
            errors: list[Exception] = []

            for chunk_number, chunk in enumerate(chunks, 1):
                try:
                    self.logger.debug(
                        "Generating metadata with '%s' for chunk %d/%d",
                        get_class_name(generator),
                        chunk_number,
                        len(chunks),
                    )
                    start_time = time.perf_counter()
                    metadata = generator.generate_metadata(text=text, chunk_text=chunk.text)

                    # Validate that metadata is a dictionary
                    if not isinstance(metadata, dict):
                        raise TypeError(
                            f"Metadata generator '{get_class_name(generator)}' must return a dict, "
                            f"but returned {type(metadata).__name__}: {metadata!r}."
                        )

                    chunk.metadata.update(metadata)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    self.logger.debug(
                        "Metadata generated with '%s' for chunk %d/%d (%.2fms, %d fields)",
                        get_class_name(generator),
                        chunk_number,
                        len(chunks),
                        duration_ms,
                        len(metadata),
                    )
                except Exception as e:
                    errors.append(e)

            if errors:
                raise ExceptionGroup(
                    f"Metadata generation with '{get_class_name(generator)}' failed for some chunks", errors
                )

            generator_duration_ms = (time.perf_counter() - generator_start_time) * 1000
            self.logger.debug(
                "Metadata generation with '%s' completed in %.2fms for %d chunks",
                get_class_name(generator),
                generator_duration_ms,
                len(chunks),
            )

        total_duration_ms = (time.perf_counter() - total_start_time) * 1000
        self.logger.debug(
            "All metadata generation completed in %.2fms for %d chunks with %d generators",
            total_duration_ms,
            len(chunks),
            len(self.metadata_generators),
        )

        return chunks

    def split(self, text_or_path: str | Path, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        """Split text or file content into chunks using the appropriate splitter.

        This method automatically detects whether the input is a file path or text content,
        selects the appropriate splitter, and returns a list of chunks with merged metadata.

        Args:
            text_or_path: Either a Path object pointing to a file, or a string containing
                         text content to be split. If a Path is provided, the file will be
                         read and split according to its extension. If a string is provided,
                         it will be treated as text content.
            metadata: Optional dictionary of metadata to attach to all chunks. This metadata
                     will be merged with any chunk-specific metadata, with chunk-specific
                     metadata taking precedence in case of key conflicts.

        Returns:
            A list of Chunk objects, each containing:
            - text: The chunk content
            - token_count: Number of tokens in the chunk
            - metadata: Combined metadata from both the provided metadata and chunk-specific metadata

        Raises:
            FileNotFoundError: If a Path is provided but the file doesn't exist.
            UnicodeDecodeError: If the file cannot be decoded as UTF-8.
            ValueError: If no appropriate splitter is found for the file type.
            ExceptionGroup: If metadata generation fails for any chunks (when metadata
                generators are configured). Contains all individual exceptions that occurred.

        Example:
            Split a markdown file:
            >>> chunker = Chunker()
            >>> chunks = chunker.split(Path("document.md"), metadata={"source": "docs"})
            >>> print(f"Created {len(chunks)} chunks")

            Split text directly:
            >>> text = "# Title\\n\\nSome content here."
            >>> chunks = chunker.split(text, metadata={"author": "Alice"})
        """
        text, chunks = self._split_impl(text_or_path, metadata)
        return self._add_metadata(text, chunks)
