"""
Example: Document Parsing with Unsiloed SDK (Async)

This example demonstrates how to parse documents using the async Unsiloed SDK.
"""

import os
import asyncio
from unsiloed_sdk import AsyncUnsiloedClient

# Initialize API key from environment
API_KEY = os.getenv("UNSILOED_API_KEY", "your-api-key-here")


async def basic_parse_example():
    """Basic document parsing example."""
    print("\n=== Basic Parse Example ===")

    async with AsyncUnsiloedClient(api_key=API_KEY) as client:
        # Parse a document and wait for results
        result = await client.parse_and_wait(
            file="sample.pdf",  # Replace with your file path
            merge_tables=True
        )

        print(f"Status: {result.status}")
        print(f"Total chunks: {result.total_chunks}")
        print(f"Credit used: {result.credit_used}")

        # Display first few chunks
        for i, chunk in enumerate(result.chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"  Page: {chunk.get('page_number')}")
            print(f"  Segments: {len(chunk.get('segments', []))}")


async def manual_polling_example():
    """Manual polling example."""
    print("\n=== Manual Polling Example ===")

    async with AsyncUnsiloedClient(api_key=API_KEY) as client:
        # Start parsing (non-blocking)
        response = await client.parse(
            file="document.pdf",
            merge_tables=True,
            use_high_resolution=True
        )

        print(f"Job ID: {response.job_id}")
        print(f"Initial status: {response.status}")

        # Poll manually with custom logic
        while True:
            result = await client.get_parse_result(job_id=response.job_id)
            print(f"Current status: {result.status}")

            if result.status in ["Succeeded", "Failed", "completed", "failed"]:
                break

            await asyncio.sleep(2)  # Wait 2 seconds before next check

        if result.status in ["Succeeded", "completed"]:
            print(f"Total chunks: {result.total_chunks}")


async def advanced_parse_example():
    """Advanced parsing with custom configuration."""
    print("\n=== Advanced Parse Example ===")

    async with AsyncUnsiloedClient(api_key=API_KEY) as client:
        result = await client.parse_and_wait(
            file="contract.pdf",
            merge_tables=True,
            enhanced_table=True,
            validate_table_segments=True,
            use_high_resolution=True,
            ocr_mode="auto_ocr",
            segmentation_method="smart_layout_detection",
            keep_segment_types="Text,Table,Picture",
            segment_analysis={
                "Table": {
                    "html": "LLM",
                    "markdown": "LLM",
                    "extended_context": True,
                    "crop_image": "All"
                },
                "Picture": {
                    "crop_image": "All",
                    "html": "LLM",
                    "markdown": "LLM"
                }
            }
        )

        print(f"Status: {result.status}")
        print(f"Total chunks: {result.total_chunks}")

        # Process tables
        for chunk in result.chunks:
            for segment in chunk.get('segments', []):
                if segment.get('segment_type') == 'Table':
                    print(f"\nFound table on page {chunk.get('page_number')}")
                    if 'markdown' in segment:
                        print(f"Markdown content: {segment['markdown'][:100]}...")


async def parse_from_url_example():
    """Parse document from URL."""
    print("\n=== Parse from URL Example ===")

    async with AsyncUnsiloedClient(api_key=API_KEY) as client:
        result = await client.parse_and_wait(
            url="https://example.com/sample.pdf",
            merge_tables=True
        )

        print(f"Status: {result.status}")
        print(f"File name: {result.file_name}")
        print(f"Total chunks: {result.total_chunks}")


async def parse_with_filtering_example():
    """Parse with segment type filtering."""
    print("\n=== Parse with Filtering Example ===")

    async with AsyncUnsiloedClient(api_key=API_KEY) as client:
        # Only extract specific segment types
        result = await client.parse_and_wait(
            file="document.pdf",
            keep_segment_types="Text,Table",  # Only keep text and tables
            merge_tables=True
        )

        # Count segment types
        segment_counts = {}
        for chunk in result.chunks:
            for segment in chunk.get('segments', []):
                seg_type = segment.get('segment_type')
                segment_counts[seg_type] = segment_counts.get(seg_type, 0) + 1

        print(f"Segment counts: {segment_counts}")


async def concurrent_parsing_example():
    """Parse multiple documents concurrently."""
    print("\n=== Concurrent Parsing Example ===")

    async with AsyncUnsiloedClient(api_key=API_KEY) as client:
        # Start multiple parse jobs concurrently
        files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

        # Start all jobs at once
        tasks = [client.parse(file=f) for f in files]
        responses = await asyncio.gather(*tasks)

        print(f"Started {len(responses)} parse jobs")

        # Wait for all to complete
        results = await asyncio.gather(*[
            client.parse_and_wait(file=f) for f in files
        ])

        for i, result in enumerate(results):
            print(f"{files[i]}: {result.status} - {result.total_chunks} chunks")


async def main():
    """Run all examples."""
    try:
        # Uncomment the examples you want to run
        await basic_parse_example()
        # await manual_polling_example()
        # await advanced_parse_example()
        # await parse_from_url_example()
        # await parse_with_filtering_example()
        # await concurrent_parsing_example()

        print("\nExamples completed successfully!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
