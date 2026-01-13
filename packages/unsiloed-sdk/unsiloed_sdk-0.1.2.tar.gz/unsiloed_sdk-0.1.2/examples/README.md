# Unsiloed SDK Examples

This directory contains example scripts demonstrating how to use the Unsiloed SDK for various document processing tasks.

## Setup

1. Install the SDK:
   ```bash
   pip install unsiloed-sdk
   ```

2. Set your API key:
   ```bash
   export UNSILOED_API_KEY="your-api-key-here"
   ```

3. Run an example:
   ```bash
   python parse_example.py
   ```

## Examples

### parse_example.py
Demonstrates document parsing capabilities:
- Basic parsing
- Async parsing
- Advanced parsing with custom configurations
- Parsing from URLs
- Segment type filtering

### extract_example.py
Shows how to extract structured data:
- Invoice data extraction
- Contract information extraction
- Resume/CV parsing
- Async extraction
- Extraction from URLs

### classify_example.py
Document classification examples:
- Basic classification
- Financial document classification
- Legal document classification
- Async classification
- Batch classification

### split_example.py
Document splitting examples:
- Split by sections
- Book chapter splitting
- Contract section splitting
- Form section splitting
- Medical record splitting

## Usage

Each example file contains multiple functions. Uncomment the function calls at the bottom of each file to run specific examples:

```python
if __name__ == "__main__":
    # Uncomment the examples you want to run
    basic_parse_example()
    # advanced_parse_example()
    # parse_from_url_example()
```

## Notes

- Replace file paths in examples with your actual document paths
- Ensure you have sufficient API quota for processing
- Some operations may take time depending on document size
- Check the main README for detailed API documentation
