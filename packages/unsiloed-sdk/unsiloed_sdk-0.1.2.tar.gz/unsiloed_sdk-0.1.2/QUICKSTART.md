# Quick Start Guide

Get started with the Unsiloed Python SDK in minutes!

## Installation

### From PyPI (when published)

```bash
pip install unsiloed-sdk
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/unsiloed/unsiloed-sdk-python.git
cd unsiloed-sdk-python

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

## Get Your API Key

1. Sign up at [Unsiloed](https://www.unsiloed.ai/login)
2. Navigate to the API Keys section
3. Generate a new API key
4. Save it securely

## Your First Request

### Parse a Document

Create a file called `test.py`:

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    # Initialize client
    async with UnsiloedClient(api_key="your-api-key-here") as client:
        # Parse a document
        result = await client.parse_and_wait(
            file="path/to/your/document.pdf",
            merge_tables=True
        )

        # Print results
        print(f"Status: {result.status}")
        print(f"Total chunks: {result.total_chunks}")

        # Display first chunk
        if result.chunks:
            first_chunk = result.chunks[0]
            print(f"\nFirst chunk from page {first_chunk['page_number']}:")
            for segment in first_chunk['segments']:
                content = segment.get('content', '')[:100]
                print(f"- {segment['segment_type']}: {content}")

asyncio.run(main())
```

Run it:

```bash
python test.py
```

### Extract Structured Data

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    async with UnsiloedClient(api_key="your-api-key-here") as client:
        # Define what to extract
        schema = {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string"},
                "date": {"type": "string"},
                "total": {"type": "number"}
            }
        }

        # Extract data
        result = await client.extract_and_wait(
            file="invoice.pdf",
            schema=schema
        )

        print(result.result)

asyncio.run(main())
```

### Classify a Document

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    async with UnsiloedClient(api_key="your-api-key-here") as client:
        # Classify document
        result = await client.classify_and_wait(
            file="document.pdf",
            categories=["Invoice", "Receipt", "Contract", "Letter"]
        )

        print(f"Document type: {result.result['classification']}")
        print(f"Confidence: {result.result['confidence']}")

asyncio.run(main())
```

## Environment Variables

Set up your environment for easier configuration:

```bash
export UNSILOED_API_KEY="your-api-key-here"
export UNSILOED_BASE_URL="https://prod.visionapi.unsiloed.ai"
```

Then use in your code:

```python
import os
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    client = UnsiloedClient(
        api_key=os.getenv("UNSILOED_API_KEY")
    )
    # Your code here
    await client.close()

asyncio.run(main())
```

## Using Context Managers

For automatic cleanup:

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    async with UnsiloedClient(api_key="your-api-key") as client:
        result = await client.parse_and_wait(file="document.pdf")
        print(result.chunks)
    # Client automatically closed

asyncio.run(main())
```

## Error Handling

```python
import asyncio
from unsiloed_sdk import (
    UnsiloedClient,
    AuthenticationError,
    QuotaExceededError,
    InvalidRequestError
)

async def main():
    async with UnsiloedClient(api_key="your-api-key") as client:
        try:
            result = await client.parse_and_wait(file="document.pdf")
        except AuthenticationError:
            print("Invalid API key")
        except QuotaExceededError as e:
            print(f"Quota exceeded. Remaining: {e.response_data}")
        except InvalidRequestError as e:
            print(f"Invalid request: {e.message}")

asyncio.run(main())
```

## Processing Multiple Documents Concurrently

One of the main benefits of async is concurrent processing:

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    async with UnsiloedClient(api_key="your-api-key") as client:
        # Start multiple parse jobs concurrently
        tasks = [
            client.parse(file="doc1.pdf"),
            client.parse(file="doc2.pdf"),
            client.parse(file="doc3.pdf"),
        ]

        # Wait for all jobs to start
        responses = await asyncio.gather(*tasks)
        print(f"Started {len(responses)} jobs")

        # Poll all jobs concurrently
        results = await asyncio.gather(*[
            client.get_parse_result(r.job_id) for r in responses
        ])

        for result in results:
            print(f"Job {result.job_id}: {result.status}")

asyncio.run(main())
```

## Manual vs Auto Polling

### Manual Polling (More Control)

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    async with UnsiloedClient(api_key="your-api-key") as client:
        # Start the job
        response = await client.parse(file="document.pdf")
        print(f"Job started: {response.job_id}")

        # Do other work here...

        # Check status later
        result = await client.get_parse_result(job_id=response.job_id)
        print(f"Status: {result.status}")

asyncio.run(main())
```

### Auto Polling (Convenience)

```python
import asyncio
from unsiloed_sdk import UnsiloedClient

async def main():
    async with UnsiloedClient(api_key="your-api-key") as client:
        # Parse and wait automatically
        result = await client.parse_and_wait(file="document.pdf")
        print(f"Done! Status: {result.status}")

asyncio.run(main())
```

## Next Steps

- Check out the [README.md](README.md) for complete documentation
- Explore the [examples/](examples/) directory for more use cases
- Visit [docs.unsiloed.ai](https://docs.unsiloed.ai) for API reference

## Common Issues

### Import Error

If you get `ModuleNotFoundError: No module named 'unsiloed_sdk'`:

```bash
pip install -e .
```

### Authentication Error

Make sure your API key is valid and active. Check the dashboard at www.unsiloed.ai/login.

### File Not Found

Use absolute paths or ensure your working directory is correct:

```python
from pathlib import Path

file_path = Path(__file__).parent / "documents" / "test.pdf"
result = await client.parse_and_wait(file=str(file_path))
```

### Async Runtime Error

Make sure you're running async functions with `asyncio.run()`:

```python
# ✅ Correct
import asyncio

async def main():
    async with UnsiloedClient(api_key="key") as client:
        result = await client.parse_and_wait(file="doc.pdf")

asyncio.run(main())

# ❌ Incorrect - This won't work
async def main():
    async with UnsiloedClient(api_key="key") as client:
        result = await client.parse_and_wait(file="doc.pdf")

main()  # Missing asyncio.run()
```

## Support

Need help?
- Email: support@unsiloed.com
- Documentation: https://docs.unsiloed.ai/
- GitHub Issues: https://github.com/unsiloed/unsiloed-sdk-python/issues
