# 🤝 Chunkmate

**Chunkmate is your friendly companion for splitting text into manageable chunks!**

A Python library for intelligently splitting text and documents into token-aware chunks. Perfect for processing different type of documents for RAG (Retrieval-Augmented Generation) systems, LLM applications, and any text processing pipeline that needs smart chunking.

## 🚀 Simple. Powerful. Just 2 Lines.

```python
chunker = Chunker()
chunks = chunker.split(Path("document.md"))  # Works with .md, .json, .html, .txt files or raw text!
```

**That's it!** Split any document (Markdown, JSON, HTML, or plain text) with automatic format detection and intelligent chunking. Pass a file `Path` or raw text string. No configuration needed. No complexity. Just results.

## Features

- 🎯 **Smart Text Splitting**: Intelligently splits text while respecting natural boundaries (paragraphs, sentences, etc.)
- 📝 **Multiple Format Support**: Built-in splitters for common document types:
  - **Markdown** (`.md`, `.mdx`, `.markdown`) - Header-aware splitting that respects document structure
  - **JSON** (`.json`) - Recursive splitting while preserving valid JSON structure
  - **HTML** (`.html`, `.htm`) - Converts to Markdown and splits by headers (h2, h3)
  - **Plain Text** (`.txt`) - Recursive character-based splitting with smart boundaries
- 🤖 **Auto-Detection**: Automatically detects text format (JSON, Markdown, HTML, plain text) when no file extension is available
- 🔢 **Token-Aware**: Counts tokens using tiktoken to ensure chunks fit within model limits
- 🧩 **Extensible**: Easy to add custom splitters for different document types
- 🎨 **Metadata Generation**: Optional metadata enrichment for each chunk (custom or AI-powered) with support for multiple generators to improve RAG retrieval with context, keywords, summaries, etc.
- ⚡ **Async Support**: `AsyncChunker` for concurrent metadata generation with rate limiting
- 📁 **File or String**: Works with both file paths and raw text strings
- 🎛️ **Configurable**: Customize chunk size and splitting behavior
- ✅ **Fully Tested**: 100% test coverage with comprehensive unit tests

## Installation

```bash
pip install chunkmate
```

Or using `uv`:

```bash
uv add chunkmate
```

**Optional Dependencies:**

For framework integrations, install with optional dependencies:

```bash
# With LangChain support
pip install chunkmate[langchain]

# With LlamaIndex support
pip install chunkmate[llamaindex]

# With all optional dependencies
pip install chunkmate[all]
```

## Quick Start

### Basic Usage

```python
from chunkmate import Chunker

# Initialize the chunker
chunker = Chunker()

# Split text directly
text = "Your long document text here..."
chunks = chunker.split(text)

# Or split from a file
from pathlib import Path
chunks = chunker.split(Path("document.md"))

# Add custom metadata to all chunks
chunks = chunker.split(text, metadata={"source": "user_input", "category": "docs"})

# Access chunk data
for chunk in chunks:
    print(f"Text: {chunk.text}")
    print(f"Tokens: {chunk.token_count}")
    print(f"Metadata: {chunk.metadata}")
```

### Metadata Generation

Enrich chunks with AI-generated metadata for better retrieval in RAG systems:

```python
from chunkmate import Chunker, MetadataGenerator

# Implement your metadata generator
class MyMetadataGenerator:
    def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Use your LLM to generate metadata for this chunk
        # text: the full document text
        # chunk_text: the specific chunk text
        # Return a dictionary with any metadata fields you want
        return {
            "context": f"This chunk discusses {chunk_text[:50]}...",
            "doc_topic": text[:50]
        }

# Create chunker with metadata generation
chunker = Chunker(metadata_generators=MyMetadataGenerator())

# Split text - metadata is automatically added to each chunk
chunks = chunker.split("Your document text")

# Each chunk now has generated metadata
for chunk in chunks:
    print(f"Text: {chunk.text}")
    print(f"Context: {chunk.metadata['context']}")
    print(f"Topic: {chunk.metadata['doc_topic']}")

# Use multiple generators to add different types of metadata
class KeywordGenerator:
    def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Extract keywords from chunk
        keywords = extract_keywords(chunk_text)
        return {"keywords": keywords, "keyword_count": len(keywords)}

chunker = Chunker(metadata_generators=[MyMetadataGenerator(), KeywordGenerator()])
chunks = chunker.split("Your document text")

# Each chunk has metadata from both generators
for chunk in chunks:
    print(f"Context: {chunk.metadata['context']}")
    print(f"Keywords: {chunk.metadata['keywords']}")

# Combine with custom metadata
chunks = chunker.split(
    "Your document text",
    metadata={"source": "user_input", "category": "docs"}
)
# Each chunk will have custom metadata + generated metadata
```

### Async Metadata Generation (Concurrent Processing)

For high-performance applications, use `AsyncChunker` to generate metadata for all chunks concurrently:

```python
from chunkmate import AsyncChunker, AsyncMetadataGenerator

# Implement your async metadata generator
class MyAsyncMetadataGenerator:
    def get_max_concurrency(self) -> int | None:
        return 5  # Limit to 5 concurrent API calls

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Use your async LLM client to generate metadata
        # AsyncChunker will call this method concurrently for all chunks
        response = await your_llm_client.generate(
            prompt=f"Summarize this chunk: {chunk_text}"
        )
        return {
            "context": response.text,
            "summary": response.summary
        }

# Create async chunker with concurrent metadata generation
chunker = AsyncChunker(metadata_generators=MyAsyncMetadataGenerator())

# Split text - metadata generation happens concurrently for all chunks
# This provides significant speedup for N chunks when calling I/O-bound APIs
async def process_document():
    chunks = await chunker.split("Your document text")
    return chunks

# With rate limiting to avoid API throttling (recommended)
# Control concurrency via get_max_concurrency() in your metadata generator
class RateLimitedGenerator:
    def get_max_concurrency(self) -> int | None:
        return 5  # Max 5 concurrent API calls

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        summary = await call_llm_api(chunk_text)
        return {"summary": summary}

chunker = AsyncChunker(metadata_generators=RateLimitedGenerator())

# This ensures you don't hit rate limits on LLM APIs
chunks = await chunker.split(Path("large_document.md"))

# Use multiple generators - each processes all chunks concurrently
class AsyncKeywordGenerator:
    def get_max_concurrency(self) -> int | None:
        return 10  # Can handle more concurrent calls

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        keywords = await extract_keywords_async(chunk_text)
        return {"keywords": keywords, "keyword_count": len(keywords)}

chunker = AsyncChunker(
    metadata_generators=[MyAsyncMetadataGenerator(), AsyncKeywordGenerator()]
)

# All generators run sequentially, but each processes all chunks concurrently
# Each generator's max_concurrency is controlled by its get_max_concurrency() method
chunks = await chunker.split("Your document text")

# Access all generated metadata
for chunk in chunks:
    print(f"Context: {chunk.metadata['context']}")
    print(f"Keywords: {chunk.metadata['keywords']}")
```

**Why AsyncChunker?**
- **Concurrent Processing**: Metadata generation for all chunks happens concurrently
- **Significant Speedup**: Process multiple chunks simultaneously—typically 5-10× faster for I/O-bound operations like LLM API calls
- **Rate Limiting**: Built-in `max_concurrency` parameter to prevent API throttling
- **Multiple Generators**: Support for multiple metadata generators, each processing all chunks concurrently
- **Error Handling**: Robust error handling with `ExceptionGroup` for failed chunks
- **Perfect for LLM APIs**: Ideal when calling OpenAI, Anthropic, or other async LLM services


### Real-World Example: OpenAI Context Generator

Here's a complete, production-ready example using OpenAI's API to generate contextual descriptions for chunks:

```python
import os
import logging
from typing import Any
from openai import AsyncOpenAI
from openai import RateLimitError, APIError
from chunkmate import AsyncChunker, AsyncMetadataGenerator

class AsyncOpenAIContextGenerator:
    def get_max_concurrency(self) -> int | None:
        return self.max_concurrency

    def __init__(
        self, api_key: str | None = None, max_concurrency: int | None = 5
    ) -> None:
        self.api_key: str = api_key if api_key else os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        # Configure with more retries for rate limit handling (default is 2)
        self.client: AsyncOpenAI = AsyncOpenAI(api_key=self.api_key, max_retries=5)
        self.model: str = "gpt-5-nano"
        self.max_concurrency: int | None = max_concurrency

    async def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        """
        Generate context metadata for a chunk using the OpenAI API.

        Uses prompt caching by passing the complete document text, which is cached
        across multiple requests for the same document, reducing costs significantly.

        Automatically retries up to 5 times on rate limits and API errors with
        exponential backoff. Returns an empty context payload on failure for
        graceful degradation.

        Args:
            text: The full document text.
            chunk_text: The specific chunk text to generate context for.

        Returns:
            dict[str, Any]: A dictionary with the 'context' key containing a brief
            2-3 sentence description, or an empty string if generation fails.
        """
        # Structure prompt to maximize caching: put the full document first (cached),
        # then the variable part (the specific chunk) last
        system_message = """You are a helpful assistant that generates brief, contextual descriptions for text chunks. Given a complete document and a specific chunk from it, provide a brief, succinct context (2-3 sentences max) that describes what this chunk is about and how it relates to the overall document."""

        user_message = f"""Complete Document:
{text}

---

For the following chunk from the above document, provide a brief context:

Chunk:
{chunk_text}

Context:"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
            )

            content = response.choices[0].message.content
            if content is None:
                logging.warning("OpenAI returned None content")
                return {"context": ""}
            return {"context": content.strip()}
        except RateLimitError as e:
            logging.warning(f"Rate limit hit: {e}")
            return {"context": ""}
        except APIError as e:
            logging.error(f"OpenAI API error: {e}")
            return {"context": ""}
        except Exception as e:
            logging.error(f"Unexpected error generating context: {e}", exc_info=True)
            return {"context": ""}


class OpenAIContextGenerator:
    def __init__(self) -> None:
        self.api_key: str = os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        # Configure with more retries for rate limit handling (default is 2)
        self.client: OpenAI = OpenAI(api_key=self.api_key, max_retries=5)
        self.model: str = "gpt-5-nano"

    def generate_metadata(self, text: str, chunk_text: str) -> dict[str, Any]:
        """
        Generate context metadata for a chunk using the OpenAI API.

        Uses prompt caching by passing the complete document text, which is cached
        across multiple requests for the same document, reducing costs significantly.

        Automatically retries up to 5 times on rate limits and API errors with
        exponential backoff. Returns an empty context payload on failure for
        graceful degradation.

        Args:
            text: The full document text.
            chunk_text: The specific chunk text to generate context for.

        Returns:
            dict[str, Any]: A dictionary with the 'context' key containing a brief
            2-3 sentence description, or an empty string if generation fails.
        """
        # Structure prompt to maximize caching: put the full document first (cached),
        # then the variable part (the specific chunk) last
        system_message = """You are a helpful assistant that generates brief, contextual descriptions for text chunks. Given a complete document and a specific chunk from it, provide a brief, succinct context (2-3 sentences max) that describes what this chunk is about and how it relates to the overall document."""

        user_message = f"""Complete Document:
{text}

---

For the following chunk from the above document, provide a brief context:

Chunk:
{chunk_text}

Context:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
            )

            content = response.choices[0].message.content
            if content is None:
                logging.warning("OpenAI returned None content")
                return {"context": ""}
            return {"context": content.strip()}
        except RateLimitError as e:
            logging.warning(f"Rate limit hit: {e}")
            return {"context": ""}
        except APIError as e:
            logging.error(f"OpenAI API error: {e}")
            return {"context": ""}
        except Exception as e:
            logging.error(f"Unexpected error generating context: {e}", exc_info=True)
            return {"context": ""}

# Usage example (Async)
async def process_document_with_openai_async():
    # Create the context generator
    # Rate limiting is controlled via get_max_concurrency() in the generator
    openai_generator = AsyncOpenAIContextGenerator()

    # Create chunker with OpenAI metadata generation
    chunker = AsyncChunker(
        metadata_generators=openai_generator
    )

    # Process your document
    chunks = await chunker.split("Your long document text here...")

    # Each chunk now has AI-generated context
    for chunk in chunks:
        print(f"Chunk: {chunk.text[:100]}...")
        print(f"Context: {chunk.metadata['context']}")
        print("---")

    return chunks

# Run the async function
import asyncio
asyncio.run(process_document_with_openai_async())

# Usage example (Sync)
def process_document_with_openai_sync():
    # Create the synchronous context generator
    openai_generator = OpenAIContextGenerator()

    # Create chunker with OpenAI metadata generation
    chunker = Chunker(
        metadata_generators=openai_generator
    )

    # Process your document
    chunks = chunker.split("Your long document text here...")

    # Each chunk now has AI-generated context
    for chunk in chunks:
        print(f"Chunk: {chunk.text[:100]}...")
        print(f"Context: {chunk.metadata['context']}")
        print("---")

    return chunks

# Run the sync function
process_document_with_openai_sync()
```

**Key Features:**
- **Prompt Caching**: Structures prompts to maximize OpenAI's caching benefits by putting the full document first (cached across requests)
- **Automatic Retries**: Configures 5 retries with exponential backoff for rate limits and API errors
- **Graceful Degradation**: Returns empty context on failure instead of crashing
- **Cost Efficient**: Using `gpt-5-nano` for cost-effective context generation
- **Rate Limit Protection**: Async version uses `max_concurrency=5` to prevent overwhelming the API
- **Production Ready**: Includes comprehensive error handling and logging
- **Flexible**: Choose async for concurrent processing or sync for simpler sequential processing

**Cost Optimization Tips:**
- The prompt structure maximizes caching - the full document is cached, reducing costs for subsequent chunks
- Adjust `max_concurrency` based on your OpenAI rate limits (async version only)



### Auto-Detection of Text Format

When splitting text directly (without a file extension), Chunkmate automatically detects the format:

```python
from chunkmate import Chunker

chunker = Chunker()

# JSON content is automatically detected
json_text = '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}'
chunks = chunker.split(json_text)
# Uses JSONSplitter automatically

# HTML content is automatically detected
html_text = """
<html>
<body>
    <h1>Welcome</h1>
    <p>This is HTML content.</p>
</body>
</html>
"""
chunks = chunker.split(html_text)
# Uses HTMLSplitter automatically

# Markdown content is automatically detected
markdown_text = """
## Introduction
This is a markdown document.

### Features
- Feature 1
- Feature 2
"""
chunks = chunker.split(markdown_text)
# Uses MarkdownSplitter automatically

# Plain text is handled by TextSplitter
plain_text = "This is just plain text without any special formatting."
chunks = chunker.split(plain_text)
# Uses TextSplitter automatically
```

### Custom Splitters

Create your own splitter for specific document types:

```python
from chunkmate import Chunker, Splitter, Chunk
import csv
from io import StringIO

class CSVSplitter(Splitter):
    def __init__(self, max_chunk_size: int = 512, rows_per_chunk: int = 100):
        self.max_chunk_size = max_chunk_size
        self.rows_per_chunk = rows_per_chunk

    def split(self, text: str) -> list[Chunk]:
        """Split CSV into chunks, each containing a batch of rows with header."""
        reader = csv.reader(StringIO(text))
        rows = list(reader)

        if not rows:
            return []

        header = rows[0]
        data_rows = rows[1:]
        chunks = []

        # Split data into batches, each with the header
        for i in range(0, len(data_rows), self.rows_per_chunk):
            batch = [header] + data_rows[i:i + self.rows_per_chunk]
            chunk_text = '\n'.join(','.join(row) for row in batch)
            chunks.append(Chunk(
                text=chunk_text,
                token_count=len(chunk_text.split()),
                metadata={"rows": len(batch) - 1, "has_header": True}
            ))

        return chunks

    def can_handle(self, text: str) -> bool:
        """Detect if text is CSV format by checking for comma-separated structure."""
        try:
            lines = text.strip().split('\n')
            if len(lines) < 2:
                return False

            # Check if at least 80% of lines have the same number of commas
            comma_counts = [line.count(',') for line in lines[:10]]
            if not comma_counts or comma_counts[0] == 0:
                return False

            consistent = sum(1 for c in comma_counts if c == comma_counts[0])
            return consistent / len(comma_counts) >= 0.8
        except:
            return False

# Register your custom splitter
chunker = Chunker(
    splitters={"csv": CSVSplitter(rows_per_chunk=50)},
    extension_map={"csv": "csv", "tsv": "csv"}
)

# Now .csv files will use your custom splitter
chunks = chunker.split(Path("data.csv"))

# CSV text is auto-detected too!
csv_text = """name,age,city
Alice,30,NYC
Bob,25,LA
Charlie,35,Chicago"""
chunks = chunker.split(csv_text)  # Automatically uses CSVSplitter
print(f"Split into {len(chunks)} chunks")
print(f"First chunk has {chunks[0].metadata['rows']} rows")
```

**Important**: The order of splitters matters for auto-detection. When registering custom splitters, more specialized splitters should be added before general-purpose ones. `TextSplitter` should always be last as it accepts any text format.

### Configure Chunk Size

```python
from chunkmate import TextSplitter, MarkdownSplitter, Chunker

# Create splitters with custom chunk sizes
text_splitter = TextSplitter(max_chunk_size=1024)
markdown_splitter = MarkdownSplitter(max_chunk_size=1024)

# Use in chunker
chunker = Chunker(
    splitters={
        "text": text_splitter,
        "markdown": markdown_splitter,
    }
)
```

### Custom Token Counting

By default, Chunkmate uses `o200k_base` encoding (for GPT-4o/GPT-4o-mini or newer models). For older models, provide a custom token counter:

```python
import tiktoken
from chunkmate import TextSplitter

# For GPT-4, GPT-3.5-turbo, or text-embedding models
def cl100k_counter(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

splitter = TextSplitter(
    max_chunk_size=512,
    count_tokens=cl100k_counter
)

# Or use a simple word-based counter
def word_counter(text: str) -> int:
    return len(text.split())

splitter = TextSplitter(count_tokens=word_counter)
```

**Encoding Compatibility:**
- `o200k_base` (default): GPT-4o, GPT-4o-mini, GPT-5, GPT-5-mini, GPT-5-nano
- `cl100k_base`: GPT-4, GPT-4-turbo, GPT-3.5-turbo, text-embedding-3-*
- `p50k_base`: GPT-3 models (Davinci, Curie, etc.)

### Convert to Other Formats

Chunkmate provides converters to integrate with popular frameworks:

```python
from chunkmate import Chunker, chunks_to_langchain, chunks_to_llamaindex, chunks_to_dict

chunker = Chunker()
chunks = chunker.split("Your document text here...")

# Convert to LangChain documents
langchain_docs = chunks_to_langchain(chunks)
# Returns: list[langchain_core.documents.Document]

# Convert to LlamaIndex documents
llamaindex_docs = chunks_to_llamaindex(chunks)
# Returns: list[llama_index.core.schema.Document]

# Convert to plain dictionaries (for JSON serialization, databases, etc.)
chunk_dicts = chunks_to_dict(chunks)
# Returns: list[dict] with keys: text, token_count, metadata
# Example output: [
#     {'text': 'Hello', 'token_count': 1, 'metadata': {'section': 'intro'}},
#     {'text': 'World', 'token_count': 1, 'metadata': {'section': 'body'}}
# ]
```

**Installation with Optional Dependencies:**

```bash
# Install with LangChain support
pip install chunkmate[langchain]

# Install with LlamaIndex support
pip install chunkmate[llamaindex]

# Install with both LangChain and LlamaIndex
pip install chunkmate[all]

# Using uv
uv add chunkmate[langchain]
uv add chunkmate[llamaindex]
uv add chunkmate[all]
```

## Supported File Types

By default, Chunkmate supports:

- **Markdown**: `.md`, `.mdx`, `.markdown` - Uses header-aware splitting
- **JSON**: `.json` - Uses recursive JSON splitting while preserving structure
- **HTML**: `.html`, `.htm` - Uses header-aware HTML splitting
- **Text**: `.txt` - Uses recursive character splitting

### Auto-Detection

When processing raw text strings (no file extension), Chunkmate automatically detects the format:

- **JSON Detection**: Checks if text is valid JSON (objects or arrays)
- **Markdown Detection**: Checks for headers (`#`), code blocks (` ``` `), links, lists, and other markdown patterns (requires 2+ indicators)
- **HTML Detection**: Checks for HTML tags, attributes, document structure (requires 3+ indicators)
- **Text Fallback**: If no specific format is detected, falls back to plain text splitting

The detection uses a scoring system that requires multiple format indicators to avoid false positives. The order matters: JSON is checked first, then Markdown, then HTML, and finally Text as a universal fallback. This ensures Markdown files with embedded HTML are correctly detected as Markdown.

You can easily add support for more file types using custom splitters and extension mappings. When implementing custom splitters, make sure to implement the `can_handle()` method for automatic format detection.

## API Reference

### `Chunker`

Main class for chunking documents (synchronous).

```python
Chunker(
    splitters: dict[str, Splitter] | None = None,
    extension_map: dict[str, str] | None = None,
    logger: logging.Logger | None = None,
    metadata_generators: list[MetadataGenerator] | MetadataGenerator | None = None
)
```

**Parameters:**
- `splitters`: Optional dict of custom splitters to add or override defaults
- `extension_map`: Optional dict mapping file extensions to splitter types
- `logger`: Optional logger for debugging and operation tracking
- `metadata_generators`: Optional MetadataGenerator instance or list of MetadataGenerator instances for enriching chunks with metadata. Multiple generators are applied sequentially, with each adding different metadata fields to the chunks

**Methods:**
- `split(text: str | Path, metadata: dict | None = None) -> list[Chunk]`: Split text or file into chunks with optional metadata generation

**Example:**
```python
from chunkmate import Chunker, MetadataGenerator

class ContextGenerator:
    def generate_metadata(self, text: str, chunk_text: str) -> dict:
        return {"context": f"Summary: {chunk_text[:100]}"}

# Single generator
chunker = Chunker(metadata_generators=ContextGenerator())
chunks = chunker.split("document.md")

# Multiple generators
chunker = Chunker(metadata_generators=[
    ContextGenerator(),
    KeywordGenerator()
])
chunks = chunker.split("document text")
# Each chunk has metadata from all generators
```

### `AsyncChunker`

Async version of Chunker with concurrent metadata generation and rate limiting.

```python
AsyncChunker(
    splitters: dict[str, Splitter] | None = None,
    extension_map: dict[str, str] | None = None,
    logger: logging.Logger | None = None,
    metadata_generators: list[AsyncMetadataGenerator] | AsyncMetadataGenerator | None = None,
    max_concurrency: int | None = None
)
```

**Parameters:**
- `splitters`: Optional dict of custom splitters to add or override defaults
- `extension_map`: Optional dict mapping file extensions to splitter types
- `logger`: Optional logger for debugging and operation tracking
- `metadata_generators`: Optional AsyncMetadataGenerator instance or list of AsyncMetadataGenerator instances for concurrent metadata enrichment. Multiple generators are applied sequentially, with each processing all chunks concurrently
- `max_concurrency`: Optional maximum number of concurrent metadata generation tasks per generator (recommended: 3-10 for LLM APIs)

**Methods:**
- `async split(text: str | Path, metadata: dict | None = None) -> list[Chunk]`: Split text or file into chunks with concurrent metadata generation

**Key Benefits:**
- **Concurrent Processing**: All chunks are processed concurrently for metadata generation, providing significant speedup when calling I/O-bound services (like LLM APIs)
- **Rate Limiting**: Use `max_concurrency` to avoid API throttling (applied per generator)
- **Multiple Generators**: Support for multiple metadata generators, each adding different metadata fields
- **Error Handling**: Uses `ExceptionGroup` to report all metadata generation failures

**Example:**
```python
from chunkmate import AsyncChunker, AsyncMetadataGenerator

class ContextGenerator:
    def get_max_concurrency(self) -> int | None:
        return 5

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        context = await llm.generate(f"Summarize: {chunk_text}")
        return {"context": context}

class KeywordGenerator:
    def get_max_concurrency(self) -> int | None:
        return 10

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        keywords = await extract_keywords(chunk_text)
        return {"keywords": keywords}

# Use multiple generators with rate limiting
chunker = AsyncChunker(
    metadata_generators=[ContextGenerator(), KeywordGenerator()],
    max_concurrency=5  # Max 5 concurrent API calls per generator
)

chunks = await chunker.split("document.md")
# Each chunk has both 'context' and 'keywords' in metadata
```



### `Chunk`

Data class representing a text chunk.

**Attributes:**
- `text: str`: The chunk text
- `token_count: int`: Number of tokens in the chunk
- `metadata: dict`: Additional metadata (e.g., context, headers, source)

### `MarkdownSplitter`

Splits markdown documents respecting header structure. Automatically detects markdown content by looking for headers, code blocks, lists, and other markdown patterns.

```python
MarkdownSplitter(
    max_chunk_size: int = 512,
    count_tokens: Callable[[str], int] = default_token_counter
)
```

**Methods:**
- `split(text: str) -> list[Chunk]`: Split markdown text into chunks
- `can_handle(text: str) -> bool`: Returns `True` if text contains 2+ markdown patterns

### `JSONSplitter`

Splits JSON documents recursively while preserving valid JSON structure in each chunk. Ensures each chunk contains valid, parseable JSON.

```python
JSONSplitter(
    max_chunk_size: int = 512,
    count_tokens: Callable[[str], int] = default_token_counter
)
```

**Methods:**
- `split(text: str) -> list[Chunk]`: Split JSON text into chunks with valid JSON in each
- `can_handle(text: str) -> bool`: Returns `True` if text is valid JSON

### `HTMLSplitter`

Splits HTML documents by headers (h2, h3) while preserving document structure. Automatically detects HTML content by checking for tags, attributes, and document structure.

```python
HTMLSplitter(
    max_chunk_size: int = 512,
    count_tokens: Callable[[str], int] = default_token_counter
)
```

**Methods:**
- `split(text: str) -> list[Chunk]`: Split HTML text into chunks by header boundaries
- `can_handle(text: str) -> bool`: Returns `True` if text contains 3+ HTML indicators

### `TextSplitter`

Splits plain text using recursive character splitting. Acts as a universal fallback that can handle any text.

```python
TextSplitter(
    max_chunk_size: int = 512,
    count_tokens: Callable[[str], int] = default_token_counter
)
```

**Methods:**
- `split(text: str) -> list[Chunk]`: Split text into chunks
- `can_handle(text: str) -> bool`: Always returns `True` (accepts any text)

### `Splitter` Protocol

All splitters must implement this protocol:

**Methods:**
- `split(text: str) -> list[Chunk]`: Split text into chunks
- `can_handle(text: str) -> bool`: Determine if the splitter can handle the given text format

### `MetadataGenerator` Protocol

Protocol for implementing synchronous metadata generators that enrich chunks with additional information.

**Attributes:**
- `name`: A unique identifier for this generator (e.g., "context", "keywords", "summary")

**Methods:**
- `generate_metadata(text: str, chunk_text: str) -> dict`: Generate metadata for a chunk. Returns a dictionary that will be merged into the chunk's metadata

**Example Implementation:**
```python
from chunkmate import MetadataGenerator

class MyMetadataGenerator:
    def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Your custom logic here - typically calling an LLM
        context = f"This chunk is from a document about: {text[:100]}..."
        summary = chunk_text[:50]
        return {
            "context": context,
            "summary": summary,
            "length": len(chunk_text)
        }
```

**Using Multiple Generators:**
```python
class ContextGenerator:
    def generate_metadata(self, text: str, chunk_text: str) -> dict:
        return {"context": generate_context(chunk_text)}

class KeywordGenerator:
    def generate_metadata(self, text: str, chunk_text: str) -> dict:
        keywords = extract_keywords(chunk_text)
        return {"keywords": keywords, "keyword_count": len(keywords)}

# Apply both generators
chunker = Chunker(metadata_generators=[ContextGenerator(), KeywordGenerator()])
chunks = chunker.split("document text")
# Each chunk will have 'context', 'keywords', and 'keyword_count' in metadata
```

### `AsyncMetadataGenerator` Protocol

Protocol for implementing async metadata generators for use with `AsyncChunker`.

**Attributes:**
- `name`: A unique identifier for this generator (e.g., "context", "keywords", "summary")
- `max_concurrency`: Optional maximum number of concurrent calls for this specific generator. If set, limits concurrent metadata generation. If None or not set, all chunks are processed concurrently without limits.

**Methods:**
- `async generate_metadata(text: str, chunk_text: str) -> dict`: Asynchronously generate metadata for a chunk. Returns a dictionary that will be merged into the chunk's metadata

**Example Implementation:**
```python
from chunkmate import AsyncMetadataGenerator

class MyAsyncMetadataGenerator:
    def get_max_concurrency(self) -> int | None:
        return 5  # Limit to 5 concurrent API calls

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Use async LLM client for metadata generation
        # AsyncChunker calls this method once per chunk, processing all chunks concurrently
        response = await your_llm_client.generate(
            prompt=f"Summarize: {chunk_text[:200]}"
        )
        keywords = await extract_keywords_async(chunk_text)
        return {
            "context": response.text,
            "keywords": keywords,
            "summary": response.summary
        }
```

**Using Multiple Async Generators with Rate Limiting:**
```python
class AsyncContextGenerator:
    def get_max_concurrency(self) -> int | None:
        return 5  # Limit to 5 concurrent API calls

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        context = await llm.generate(f"Context for: {chunk_text}")
        return {"context": context}

class AsyncEmbeddingGenerator:
    def get_max_concurrency(self) -> int | None:
        return 10  # Can handle more concurrent calls

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        embedding = await embed_text(chunk_text)
        return {"embedding": embedding}

# Apply both generators, each with its own concurrency limit
chunker = AsyncChunker(
    metadata_generators=[AsyncContextGenerator(), AsyncEmbeddingGenerator()]
)

chunks = await chunker.split("document text")
# Each chunk will have 'context' and 'embedding' in metadata
```

**Controlling Concurrency Per Generator:**

Each generator defines its own rate limit via the `max_concurrency` attribute. This is crucial when calling external APIs with different rate limits:

```python
class SlowAPIGenerator:
    def get_max_concurrency(self) -> int | None:
        return 3  # This API has strict rate limits

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Calls to expensive/rate-limited API
        result = await slow_llm_api.generate(chunk_text)
        return {"context": result}

class FastLocalGenerator:
    def get_max_concurrency(self) -> int | None:
        return 50  # Local processing can handle more concurrency

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        # Fast local embedding generation
        embedding = await local_embedder.embed(chunk_text)
        return {"embedding": embedding}

# Each generator uses its own concurrency limit
chunker = AsyncChunker(
    metadata_generators=[SlowAPIGenerator(), FastLocalGenerator()]
)

chunks = await chunker.split("document text")
# SlowAPIGenerator processes with max 3 concurrent calls
# FastLocalGenerator processes with max 50 concurrent calls

# Generators can return None for unlimited concurrency
class UnlimitedGenerator:
    def get_max_concurrency(self) -> int | None:
        return None  # No rate limiting

    async def generate_metadata(self, text: str, chunk_text: str) -> dict:
        return {"data": await fast_local_operation(chunk_text)}
```

### Converter Functions

**`chunks_to_langchain(chunks: list[Chunk]) -> list[Document]`**

Converts Chunkmate chunks to LangChain documents. Requires `langchain-core` to be installed.

**`chunks_to_llamaindex(chunks: list[Chunk]) -> list[Document]`**

Converts Chunkmate chunks to LlamaIndex documents. Requires `llama-index-core` to be installed.

**`chunks_to_dict(chunks: list[Chunk]) -> list[dict]`**

Converts Chunkmate chunks to plain dictionaries. Useful for JSON serialization, database storage, API integration, or working with frameworks that aren't directly supported. Each dictionary contains `text`, `token_count`, and `metadata` keys. No additional dependencies required.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/gvre/chunkmate.git
cd chunkmate

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/chunkmate --cov-report=html

# Run linter
uv run ruff check .

# Format code
uv run ruff format .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_chunker.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov

# Run with coverage report
uv run pytest --cov=src/chunkmate --cov-report=html
# Open htmlcov/index.html to view detailed coverage report
```

**Test Coverage**: The project maintains 100% test coverage for core functionality, including:
- All chunker implementations (`Chunker`, `AsyncChunker`)
- All splitters (Markdown, JSON, HTML, Text)
- Context generation (sync and async)
- Rate limiting and concurrent processing
- Error handling and edge cases

## Why Chunkmate?

When you need to split text, you need a reliable companion. Someone who can handle any document and split it into perfect chunks with ease. That's Chunkmate - your friendly text chunking mate.

**Chunkmate makes text splitting simple, intelligent, and effortless.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Author

**Giannis Vrentzos** - [gvre@gvre.gr](mailto:gvre@gvre.gr)

## Acknowledgments

- Built on top of [LangChain Text Splitters](https://github.com/langchain-ai/langchain)
- Token counting powered by [tiktoken](https://github.com/openai/tiktoken)
- **Note**: The core library was designed and hand-written by the author. Tests, documentation (docstrings), and this README were AI-generated.

---

*Remember: With Chunkmate, you're never alone in your text processing journey.*
