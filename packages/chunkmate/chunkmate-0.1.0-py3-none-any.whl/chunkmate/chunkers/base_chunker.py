import logging
from pathlib import Path
from typing import Any, ClassVar

from chunkmate.chunkers.chunk import Chunk
from chunkmate.splitters import HTMLSplitter, JSONSplitter, MarkdownSplitter, Splitter, TextSplitter
from chunkmate.utils.reflection import get_class_name
from chunkmate.utils.tokens import total_tokens


class BaseChunker:
    """Base class containing shared logic for Chunker and AsyncChunker.

    This class provides common functionality for document chunking, including:
    - Splitter management and registration
    - File extension to splitter type mapping
    - Splitter selection logic
    - File reading and text splitting

    Subclasses should implement metadata generation logic appropriate for
    their execution model (sync or async).

    Attributes:
        _EXTENSIONS_TYPE_MAP: Default mapping of file extensions to splitter types.
        _DEFAULT_SPLITTERS: Default splitter classes for supported document types.
    """

    _EXTENSIONS_TYPE_MAP: ClassVar[dict[str, str]] = {
        "md": "markdown",
        "mdx": "markdown",
        "markdown": "markdown",
        "txt": "text",
        "json": "json",
        "html": "html",
        "htm": "html",
    }

    _DEFAULT_SPLITTERS: ClassVar[dict[str, type[Splitter]]] = {
        "json": JSONSplitter,
        "markdown": MarkdownSplitter,
        "html": HTMLSplitter,
        "text": TextSplitter,
    }

    def __init__(
        self,
        splitters: dict[str, Splitter] | None = None,
        extension_map: dict[str, str] | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialize the base chunker with splitters and extension mappings.

        Args:
            splitters: Optional dictionary mapping splitter type names to Splitter instances.
                      These will be added to or override the default splitters.
                      Keys should match the splitter type names (e.g., "markdown", "text").
            extension_map: Optional dictionary mapping file extensions to splitter type names.
                          This allows custom file extensions to be associated with existing
                          splitter types. All mapped types must have corresponding splitters.
            logger: Optional logger instance for logging chunking operations.
                   If not provided, uses the default logger for this module.

        Raises:
            ValueError: If an extension in extension_map maps to a splitter type that
                       doesn't exist in the available splitters.
        """
        # Initialize with default splitters (instantiated)
        self._splitters: dict[str, Splitter] = {
            name: splitter_class() for name, splitter_class in self._DEFAULT_SPLITTERS.items()
        }

        # Add or override with custom splitters
        if splitters:
            self._splitters.update(splitters)

        # Allow custom extension mappings
        self._extension_map = dict(self._EXTENSIONS_TYPE_MAP)
        if extension_map:
            # Validate that all mapped types have corresponding splitters
            for ext, splitter_type in extension_map.items():
                if splitter_type not in self._splitters:
                    raise ValueError(f"Extension '{ext}' maps to unknown splitter type '{splitter_type}'")
            self._extension_map.update(extension_map)

        # Set up logger (use custom logger or default to module logger)
        self.logger = logger or logging.getLogger(__name__)

    def _get_splitter(self, text_or_extension: str) -> Splitter:
        """Get the appropriate splitter for a given extension or text type.

        This method attempts to find a splitter in two ways:
        1. By looking up the extension in the extension map
        2. By auto-detecting using each splitter's can_handle() method

        Args:
            text_or_extension: File extension (without dot) or text type identifier.

        Returns:
            The Splitter instance appropriate for the given type.

        Raises:
            ValueError: If the mapped splitter type has no registered splitter.
        """
        splitter_type = self._extension_map.get(text_or_extension.lower())
        if splitter_type is None:
            # Auto-detect splitter type based on text
            for stype, splitter in self._splitters.items():
                if splitter.can_handle(text_or_extension):
                    splitter_type = stype
                    break

        if splitter_type not in self._splitters:
            raise ValueError(
                f"No splitter registered for type '{splitter_type}'. "
                f"Available types: {', '.join(self._splitters.keys())}"
            )

        return self._splitters[splitter_type]

    def _split_impl(self, text_or_path: str | Path, metadata: dict[str, Any] | None = None) -> tuple[str, list[Chunk]]:
        """Core splitting implementation shared by sync and async chunkers.

        This method handles the common logic of:
        - Detecting if input is a file path or text
        - Reading file content if needed
        - Selecting the appropriate splitter
        - Performing the split operation
        - Merging metadata

        Args:
            text_or_path: Either a Path object pointing to a file, or a string containing
                         text content to be split.
            metadata: Optional dictionary of metadata to attach to all chunks.

        Returns:
            A tuple containing:
            - The full text that was split (for metadata generation)
            - A list of Chunk objects with merged metadata

        Raises:
            FileNotFoundError: If a Path is provided but the file doesn't exist.
            UnicodeDecodeError: If the file cannot be decoded as UTF-8.
            ValueError: If no appropriate splitter is found for the file type.
        """
        if metadata is None:
            metadata = {}

        if isinstance(text_or_path, Path):
            # Path is provided, read the file content
            file_path = text_or_path

            self.logger.debug("Reading file '%s'", file_path)
            text = file_path.read_text(encoding="utf-8")
            self.logger.debug("Read file '%s' (%d chars)", file_path, len(text))

            # Detect file type from extension and choose appropriate splitter
            extension = file_path.suffix.lower()[1:]
            splitter = self._get_splitter(extension)
            self.logger.debug("Selected splitter '%s' for .%s", get_class_name(splitter), extension)
            self.logger.debug("Starting chunking with %s splitter (%d chars)", get_class_name(splitter), len(text))

            chunks = splitter.split(text)

            self.logger.debug(
                "Chunking complete: %d chunks, %d total tokens (splitter: %s)",
                len(chunks),
                total_tokens(chunks),
                get_class_name(splitter),
            )

            # Merge metadata
            merged_chunks = [
                Chunk(text=c.text, token_count=c.token_count, metadata={**metadata, **c.metadata}) for c in chunks
            ]

            return text, merged_chunks
        else:
            # Text content is provided directly
            text = text_or_path
            splitter = self._get_splitter(text)
            self.logger.debug("Selected splitter '%s' (auto-detected)", get_class_name(splitter))
            self.logger.debug("Starting chunking with %s splitter (%d chars)", get_class_name(splitter), len(text))

            chunks = splitter.split(text)

            self.logger.debug(
                "Chunking complete: %d chunks, %d total tokens (splitter: %s)",
                len(chunks),
                total_tokens(chunks),
                get_class_name(splitter),
            )

            # Merge metadata
            merged_chunks = [
                Chunk(text=c.text, token_count=c.token_count, metadata={**metadata, **c.metadata}) for c in chunks
            ]

            return text, merged_chunks
