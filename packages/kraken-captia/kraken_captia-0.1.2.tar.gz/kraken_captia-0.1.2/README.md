# Kraken SDK for Python

Official Python SDK for the Kraken document processing API.

## Requirements

- Python 3.9 or higher
- `httpx` for HTTP requests
- `pydantic` for data validation

## Installation

```bash
pip install kraken-sdk
```

Or install from source:

```bash
git clone https://github.com/Capt-IA/Kraken-SDK.git
cd Kraken-SDK/kraken-sdk-python
pip install -e .
```

## Quick Start

```python
from kraken_sdk import KrakenClient

# Initialize the client
client = KrakenClient(
    api_key="your-api-key",
    base_url="https://api.kraken.example.com"  # Optional
)

# Check service health
health = client.info.health()
print(health.status)

# Upload a document
source = client.sources.upload("path/to/document.pdf")
print(f"Uploaded: {source.id}")

# Create an extraction job
job = client.jobs.create_single(
    task_type="extraction",
    source_id=source.id,
    ai_provider="openai",
    provider_model="gpt-4o"
)

# Wait for completion and get results
result = client.jobs.wait(job.job_id)
tasks = client.jobs.tasks(job.job_id)
print(tasks.tasks[0].result.content)
```

## Async Support

The SDK provides full async support:

```python
import asyncio
from kraken_sdk import AsyncKrakenClient

async def main():
    async with AsyncKrakenClient(api_key="your-api-key") as client:
        source = await client.sources.upload("document.pdf")
        job = await client.jobs.create_single(
            task_type="extraction",
            source_id=source.id,
            ai_provider="openai",
            provider_model="gpt-4o"
        )
        result = await client.jobs.wait(job.job_id)
        print(result)

asyncio.run(main())
```

## Structured Annotation

Extract structured data using custom schemas:

```python
from kraken_sdk import KrakenClient

client = KrakenClient(api_key="your-api-key")

annotation_schema = {
    "Invoice": {
        "general_prompt": "Invoice information",
        "is_list": False,
        "is_optional": False,
        "table_fields": [
            {"class_name": "invoice_number", "type": "str", "prompt": "The invoice number"},
            {"class_name": "total_amount", "type": "str", "prompt": "The total amount"},
            {"class_name": "date", "type": "str", "prompt": "The invoice date"}
        ]
    }
}

job = client.jobs.create_single(
    task_type="annotation",
    source_id=source.id,
    ai_provider="openai",
    provider_model="gpt-4o",
    annotation_config={
        "annotation_schema": annotation_schema,
        "output_format": "json"
    }
)

result = client.jobs.wait(job.job_id)
```

## Bulk Processing

Process multiple documents with the same configuration:

```python
job = client.jobs.create_bulk(
    task_config={
        "task_type": "extraction",
        "ai_provider": "openai",
        "provider_model": "gpt-4o"
    },
    source_ids=["source-1", "source-2", "source-3"]
)
```

## Error Handling

```python
from kraken_sdk.exceptions import (
    KrakenError,
    KrakenAuthenticationError,
    KrakenValidationError,
    KrakenNotFoundError
)

try:
    result = client.jobs.get("invalid-id")
except KrakenNotFoundError:
    print("Job not found")
except KrakenAuthenticationError:
    print("Invalid API key")
except KrakenError as e:
    print(f"API error: {e}")
```

## API Reference

### KrakenClient

| Resource | Methods |
|----------|--------|
| `client.info` | `health()`, `get()`, `tasks()` |
| `client.auth` | `me()`, `users()`, `generate_api_key()` |
| `client.jobs` | `create()`, `create_single()`, `create_bulk()`, `list()`, `get()`, `tasks()`, `wait()` |
| `client.sources` | `upload()` |
| `client.provider_api_keys` | `create()`, `list()`, `get()`, `update()`, `delete()` |
| `client.benchmarks` | `create()`, `list()`, `get()`, `report()` |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```


