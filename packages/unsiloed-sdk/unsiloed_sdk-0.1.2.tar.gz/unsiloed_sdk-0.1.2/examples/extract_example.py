"""
Example: Data Extraction with Unsiloed SDK

This example demonstrates how to extract structured data from documents
using JSON schemas.
"""

import os
import json
from unsiloed_sdk import UnsiloedClient

# Initialize the client
API_KEY = os.getenv("UNSILOED_API_KEY", "your-api-key-here")
client = UnsiloedClient(api_key=API_KEY)


def invoice_extraction_example():
    """Extract data from an invoice."""
    print("\n=== Invoice Extraction Example ===")

    # Define schema for invoice data
    schema = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "The invoice number or ID"
            },
            "invoice_date": {
                "type": "string",
                "description": "Date the invoice was issued"
            },
            "due_date": {
                "type": "string",
                "description": "Payment due date"
            },
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"}
                }
            },
            "customer": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"}
                }
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"}
                    }
                }
            },
            "subtotal": {"type": "number"},
            "tax": {"type": "number"},
            "total": {"type": "number"}
        },
        "required": ["invoice_number", "total"]
    }

    # Extract data and wait for completion
    result = client.extract_and_wait(
        file="invoice.pdf",
        schema=schema,
        confidence_threshold=0.9
    )

    if result.status == "completed":
        data = result.result
        print(f"\nInvoice Number: {data.get('invoice_number')}")
        print(f"Total: ${data.get('total')}")
        print(f"Line Items: {len(data.get('line_items', []))}")

        # Display line items
        for item in data.get('line_items', []):
            print(f"  - {item.get('description')}: ${item.get('total')}")


def contract_extraction_example():
    """Extract key information from a contract."""
    print("\n=== Contract Extraction Example ===")

    schema = {
        "type": "object",
        "properties": {
            "contract_title": {
                "type": "string",
                "description": "Title of the contract"
            },
            "parties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "role": {"type": "string", "description": "e.g., Buyer, Seller, Client, Provider"}
                    }
                }
            },
            "effective_date": {
                "type": "string",
                "description": "When the contract becomes effective"
            },
            "expiration_date": {
                "type": "string",
                "description": "When the contract expires"
            },
            "payment_terms": {
                "type": "string",
                "description": "Payment terms and conditions"
            },
            "termination_clause": {
                "type": "string",
                "description": "Conditions under which the contract can be terminated"
            },
            "key_obligations": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["contract_title", "parties"]
    }

    result = client.extract_and_wait(
        file="contract.pdf",
        schema=schema
    )

    if result.status == "completed":
        data = result.result
        print(f"\nContract: {data.get('contract_title')}")
        print(f"Parties: {data.get('parties')}")
        print(f"Effective Date: {data.get('effective_date')}")


def resume_extraction_example():
    """Extract information from a resume/CV."""
    print("\n=== Resume Extraction Example ===")

    schema = {
        "type": "object",
        "properties": {
            "personal_info": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "location": {"type": "string"}
                }
            },
            "summary": {
                "type": "string",
                "description": "Professional summary or objective"
            },
            "work_experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "position": {"type": "string"},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "responsibilities": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "institution": {"type": "string"},
                        "degree": {"type": "string"},
                        "field": {"type": "string"},
                        "graduation_date": {"type": "string"}
                    }
                }
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["personal_info"]
    }

    result = client.extract_and_wait(
        file="resume.pdf",
        schema=schema
    )

    if result.status == "completed":
        data = result.result
        print(f"\nCandidate: {data.get('personal_info', {}).get('name')}")
        print(f"Email: {data.get('personal_info', {}).get('email')}")
        print(f"Skills: {', '.join(data.get('skills', []))}")


def async_extraction_example():
    """Asynchronous extraction example."""
    print("\n=== Async Extraction Example ===")

    schema = {
        "type": "object",
        "properties": {
            "document_type": {"type": "string"},
            "date": {"type": "string"},
            "amount": {"type": "number"}
        }
    }

    # Start extraction (non-blocking)
    response = client.extract(
        file="document.pdf",
        schema=schema
    )

    print(f"Job ID: {response.job_id}")
    print(f"Status: {response.status}")

    # Later, check the result
    result = client.get_extract_result(job_id=response.job_id)

    if result.status == "completed":
        print(f"Extracted data: {json.dumps(result.result, indent=2)}")


def extract_from_url_example():
    """Extract data from a document URL."""
    print("\n=== Extract from URL Example ===")

    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "author": {"type": "string"},
            "date": {"type": "string"}
        }
    }

    result = client.extract_and_wait(
        file_url="https://example.com/document.pdf",
        schema=schema
    )

    if result.status == "completed":
        print(f"Extracted: {json.dumps(result.result, indent=2)}")


if __name__ == "__main__":
    try:
        # Run examples
        # Note: Uncomment the examples you want to run

        # invoice_extraction_example()
        # contract_extraction_example()
        # resume_extraction_example()
        # async_extraction_example()
        # extract_from_url_example()

        print("\nExamples completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
