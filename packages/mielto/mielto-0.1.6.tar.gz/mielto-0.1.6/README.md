# Mielto Python Client

Official Python client library for the Mielto API.

## Installation

```bash
pip install mielto
```

Or install from source:

```bash
cd libs/mielto_python
pip install -e .
```

## Quick Start

```python
from mielto import Mielto
from mielto.types import MemoryCreate, CollectionCreate, SearchRequest

# Initialize the client
client = Mielto(api_key="your-api-key")

# Create a memory
memory = client.memories.create(
    MemoryCreate(
        user_id="user_123",
        memory="User prefers dark mode",
        topics=["preferences", "ui"]
    )
)

# Create a collection
collection = client.collections.create(
    CollectionCreate(
        name="My Documents",
        description="Personal document collection"
    )
)

# Insert content into collection
client.collections.insert(
    collection_id=collection.id,
    file_path="document.pdf"
)

# Search in collection
results = client.collections.search(
    SearchRequest(
        query="artificial intelligence",
        collection_id=collection.id,
        max_results=10
    )
)

# Compress text
compressed = client.compress.compress(
    content="This is a long text that needs compression..."
)

# Close the client
client.close()
```

## Features

### 💬 Chat (OpenAI-Compatible)

OpenAI-compatible chat completions with intelligent context injection:

- **OpenAI SDK compatibility** - Drop-in replacement for OpenAI chat completions
- **Streaming support** - Real-time streaming responses
- **Tool/Function calling** - Full support for OpenAI function calling
- **Automatic context injection** - Retrieve and inject relevant memories and knowledge
- **Unlimited context** - No more token limits with intelligent context management
- **Multi-turn conversations** - Persistent conversation history
- Both **sync** and **async** APIs

### 🧠 Memories

Manage user memories for contextual AI interactions:

- **Create** memories from text or messages
- **Search** memories with semantic search
- **Update** and **delete** memories
- **List** memories with pagination
- **Generate** memories from conversation messages

### 📚 Collections

Organize and search your knowledge base:

- **Create** and manage collections
- **Insert** content (files, text, URLs)
- **Search** with multiple search types (semantic, hybrid, fulltext)
- **Filter** by tags, status, and metadata
- Support for multiple vector stores (pgvector, Pinecone, Qdrant)

### 🗜️ Compress

AI-powered text compression:

- Compress long texts while preserving meaning
- Support for message history compression
- Async compression with webhooks
- Includes compression metrics

## Usage Examples

### Chat Completions

The Mielto chat API is OpenAI-compatible and provides intelligent context injection:

```python
from mielto import Mielto

client = Mielto(api_key="your-api-key")

# Basic chat completion
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
```

#### Streaming Chat

```python
# Stream responses in real-time
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Tell me a story about AI"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

#### Chat with Context Injection

Automatically inject relevant memories and knowledge into your chat:

```python
# Chat with automatic context injection
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What did we discuss about Python yesterday?"}
    ],
    # Mielto-specific parameters for context injection
    user_id="user_123",
    conversation_id="conv_456",
    workspace_id="workspace_789",
    collection_ids=["knowledge_base_1", "docs_collection"]
)

print(response.choices[0].message.content)
```

#### Function/Tool Calling

Full support for OpenAI function calling:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Check if the model wants to call a function
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Function: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")
```

#### Async Chat

```python
import asyncio
from mielto import AsyncMielto

async def main():
    async with AsyncMielto(api_key="your-api-key") as client:
        # Non-streaming async chat
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Hello!"}
            ]
        )
        print(response.choices[0].message.content)
        
        # Streaming async chat
        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Count to 10"}
            ],
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

asyncio.run(main())
```

#### Using Typed Messages

```python
from mielto.types import ChatMessage

messages = [
    ChatMessage(role="system", content="You are a helpful assistant."),
    ChatMessage(role="user", content="Explain quantum computing"),
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)
```

### Memories

```python
from mielto import Mielto
from mielto.types import MemoryCreate, MemorySearchRequest

client = Mielto(api_key="your-api-key")

# Create a memory
memory = client.memories.create(
    MemoryCreate(
        user_id="user_123",
        memory="User is a software engineer specializing in Python",
        topics=["background", "skills"]
    )
)

# Search memories
results = client.memories.search(
    MemorySearchRequest(
        query="What does the user do for work?",
        user_id="user_123",
        limit=5
    )
)

for memory in results.memories:
    print(f"Memory: {memory.memory}")
    print(f"Topics: {memory.topics}")

# Generate memories from conversation
messages = [
    {"role": "user", "content": "I love Python programming"},
    {"role": "user", "content": "I work remotely from home"}
]

memories = client.memories.from_messages(
    messages=messages,
    user_id="user_123",
    topics=["preferences", "work"]
)
```

### Collections

```python
from mielto import Mielto
from mielto.types import CollectionCreate, SearchRequest

client = Mielto(api_key="your-api-key")

# Create a collection
collection = client.collections.create(
    CollectionCreate(
        name="Research Papers",
        description="AI research paper collection",
        tags=["research", "ai"]
    )
)

# Insert a file
result = client.collections.insert(
    collection_id=collection.id,
    file_path="paper.pdf",
    label="Attention Is All You Need",
    metadata={"year": 2017, "authors": ["Vaswani et al."]},
    reader="native"
)

# Check upload status
if result.is_success():
    print(f"✓ Uploaded successfully: {result.contents[0].id}")
elif result.has_failures():
    print(f"✗ Upload failed: {result.errors[0].error}")

# Insert text content
result = client.collections.insert(
    collection_id=collection.id,
    content="Transformers are a type of neural network architecture...",
    label="Transformer Notes"
)

# Insert from URL
result = client.collections.insert(
    collection_id=collection.id,
    urls=["https://arxiv.org/pdf/1706.03762.pdf"],
    reader="native"
)

# Insert entire directory
results = client.collections.insert_directory(
    collection_id=collection.id,
    directory_path="./documents",
    recursive=True,
    file_extensions=['.pdf', '.docx'],
    batch_size=10
)

# Search in collection
results = client.collections.search(
    SearchRequest(
        query="transformer architecture",
        collection_id=collection.id,
        search_type="hybrid",
        max_results=10
    )
)

for result in results.results:
    print(f"Score: {result.score}")
    print(f"Content: {result.content[:200]}...")
```

### Compress

```python
from mielto import Mielto

client = Mielto(api_key="your-api-key")

# Compress simple text
result = client.compress.compress(
    content="This is a very long piece of text that contains a lot of "
            "information about various topics. The text goes on and on "
            "with detailed explanations and examples..."
)

print(f"Original length: {result.original_length}")
print(f"Compressed length: {result.compressed_length}")
print(f"Compression time: {result.compression_time}s")
print(f"Compressed content: {result.content}")

# Compress message history
messages = [
    {"role": "user", "message": "What's the weather?", "created_at": "2024-01-01"},
    {"role": "assistant", "message": "It's sunny today!", "created_at": "2024-01-01"},
    {"role": "user", "message": "Great, thanks!", "created_at": "2024-01-01"}
]

result = client.compress.compress(
    content=messages,
    include_metadata=True
)

# Async compression with webhook
result = client.compress.compress(
    content="Long text...",
    webhook_url="https://example.com/webhook"
)
print(result.message)  # "Compression response will be sent to webhook"
```

## Async Usage

The library also provides async support:

```python
import asyncio
from mielto import AsyncMielto
from mielto.types import MemoryCreate

async def main():
    async with AsyncMielto(api_key="your-api-key") as client:
        # All the same methods, but with await
        memory = await client.memories.create(
            MemoryCreate(
                user_id="user_123",
                memory="User prefers async operations"
            )
        )
        
        results = await client.memories.search(
            MemorySearchRequest(
                query="async",
                user_id="user_123"
            )
        )

asyncio.run(main())
```

## Configuration

### API Key

You can provide your API key in multiple ways:

1. **Direct initialization**:
   ```python
   client = Mielto(api_key="your-api-key")
   ```

2. **Environment variable**:
   ```bash
   export MIELTO_API_KEY="your-api-key"
   ```
   ```python
   import os
   client = Mielto(api_key=os.getenv("MIELTO_API_KEY"))
   ```

### Custom Base URL

For self-hosted or development environments:

```python
client = Mielto(
    api_key="your-api-key",
    base_url="https://your-instance.com/v1"
)
```

### Timeout and Retries

```python
client = Mielto(
    api_key="your-api-key",
    timeout=60.0,  # seconds
    max_retries=3
)
```

## Error Handling

The library provides specific exception types:

```python
from mielto import Mielto
from mielto.client.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    PaymentRequiredError,
    CreditLimitExceededError,
    OverageLimitExceededError,
    MieltoError
)

client = Mielto(api_key="your-api-key")

try:
    memory = client.memories.get("invalid_id")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Memory not found")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except RateLimitError:
    print("Rate limit exceeded")
except PaymentRequiredError:
    print("Payment required to access this feature")
except CreditLimitExceededError:
    print("Credit limit exceeded - please upgrade your plan")
except OverageLimitExceededError:
    print("Overage limit exceeded")
except ServerError:
    print("Server error occurred")
except MieltoError as e:
    print(f"General error: {e.message}")
```

### Exception Hierarchy

- **MieltoError** (base exception)
  - **AuthenticationError** (401) - Invalid API key
  - **PaymentRequiredError** (402) - Payment required
  - **PermissionError** (403) - Insufficient permissions
  - **NotFoundError** (404) - Resource not found
  - **ValidationError** (422) - Invalid request data
  - **RateLimitError** (429) - Too many requests
  - **ServerError** (5xx) - Server-side errors
  - **TimeoutError** - Request timeout
  - **ConnectionError** - Network connection issues
  - **CreditLimitExceededError** - Credit limit reached
  - **OverageLimitExceededError** - Overage limit reached
```

## Advanced Features

### Pagination

```python
# List memories with pagination
result = client.memories.list(user_id="user_123", limit=50)

for memory in result.memories:
    print(memory.memory)

# Get next page
if result.has_more:
    next_page = client.memories.list(
        user_id="user_123",
        cursor=result.next_cursor,
        limit=50
    )
```

### Filtering Collections

```python
# Filter by tags
collections = client.collections.list(
    tags="research,ai",
    limit=20
)

# Search collections
collections = client.collections.list(
    search="machine learning",
    status="active"
)
```

### Handling Upload Responses

Upload responses include detailed status information about successes and failures:

```python
# Upload files and check status
result = client.collections.insert(
    collection_id=collection.id,
    file_path="document.pdf"
)

# Check overall status
print(f"Status: {result.status}")  # "success", "failed", or "partial_success"
print(f"Total: {result.total_uploads}")
print(f"Successful: {result.successful_uploads}")
print(f"Failed: {result.failed_uploads}")

# Use helper methods
if result.is_success():
    print("All uploads succeeded!")
elif result.has_failures():
    print("Some uploads failed!")
    
# Process successful uploads
for content in result.successful:
    print(f"✓ {content.name} - {content.id}")

# Handle failures
if result.errors:
    print("\nFailed uploads:")
    for error in result.errors:
        print(f"✗ {error.name}: {error.error}")

# Access all contents (successful and failed)
for content in result.contents:
    if content.error:
        print(f"Failed: {content.name} - {content.error}")
    else:
        print(f"Success: {content.name} - {content.id}")
```

### Batch Upload Error Handling

When uploading multiple files or a directory, handle partial failures:

```python
# Upload directory with error handling
results = client.collections.insert_directory(
    collection_id=collection.id,
    directory_path="./documents",
    batch_size=10
)

total_successful = 0
total_failed = 0

for batch in results:
    total_successful += batch.successful_uploads
    total_failed += batch.failed_uploads
    
    # Log errors for this batch
    if batch.has_failures():
        print(f"Batch had {batch.failed_uploads} failures:")
        for error in batch.errors:
            print(f"  - {error.name}: {error.error}")

print(f"\nOverall: {total_successful} succeeded, {total_failed} failed")
```

### Custom Readers for File Processing

```python
# Use specific reader for PDF processing
result = client.collections.insert(
    collection_id=collection.id,
    file_path="document.pdf",
    reader="langchain_pdfplumber"  # Better OCR for scanned PDFs
)

# Use different readers for different file types
result = client.collections.insert(
    collection_id=collection.id,
    file_path="presentation.pptx",
    reader="markitdown"  # Good for PowerPoint files
)
```

### Directory Upload

```python
# Upload entire directory
results = client.collections.insert_directory(
    collection_id=collection.id,
    directory_path="./documents",
    recursive=True,  # Include subdirectories
    batch_size=10  # Upload 10 files per batch
)

# Upload only specific file types
results = client.collections.insert_directory(
    collection_id=collection.id,
    directory_path="./documents",
    file_extensions=['.pdf', '.docx', '.txt'],
    recursive=True
)

# Upload with exclusions
results = client.collections.insert_directory(
    collection_id=collection.id,
    directory_path="./documents",
    exclude_patterns=['.DS_Store', '*.tmp', '__pycache__'],
    batch_size=5
)

# Process results
for batch in results:
    print(f"Status: {batch.status}")
    print(f"Uploaded {batch.successful_uploads}/{batch.total_uploads} files")
    
    # Show successful uploads
    for content in batch.successful:
        print(f"  ✓ {content.name}")
    
    # Show failures if any
    if batch.has_failures():
        print(f"\nFailed uploads:")
        for error in batch.errors:
            print(f"  ✗ {error.name}: {error.error}")

# Upload without progress bars (silent mode)
results = client.collections.insert_directory(
    collection_id=collection.id,
    directory_path="./documents",
    show_progress=False  # Disable progress bars
)
```

**Progress Bars**: The `insert_directory()` method automatically shows two progress bars:
- **Batch progress**: Shows batch upload progress
- **File progress**: Shows individual file processing progress

You can disable progress bars by setting `show_progress=False`.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mielto/mielto.git
cd mielto/libs/mielto_python

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff format .
ruff check .
```

### Type Checking

```bash
mypy mielto
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## License

MIT License - see LICENSE file for details.

## Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Collections API](docs/COLLECTIONS.md)** - Complete guide to collections, content management, and search
- **[Memories API](docs/MEMORIES.md)** - User memory management and contextual AI
- **[Chat API](docs/CHAT.md)** - OpenAI-compatible chat with context injection
- **[Compress API](docs/COMPRESS.md)** - AI-powered text compression
- **[Local Vectors](docs/LOCAL_VECTORS.md)** - Offline vector search and local caching

## Support

- Documentation: https://docs.mielto.com
- Issues: https://github.com/mielto/mielto/issues
- Email: hi@mielto.com

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
