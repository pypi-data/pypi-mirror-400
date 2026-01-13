"""
Example: Document Classification with Unsiloed SDK

This example demonstrates how to classify documents into categories.
"""

import os
from unsiloed_sdk import UnsiloedClient, Category

# Initialize the client
API_KEY = os.getenv("UNSILOED_API_KEY", "your-api-key-here")
client = UnsiloedClient(api_key=API_KEY)


def basic_classification_example():
    """Basic document classification example."""
    print("\n=== Basic Classification Example ===")

    # Define categories
    categories = [
        Category(name="Invoice", description="Financial invoices and billing documents"),
        Category(name="Receipt", description="Payment receipts"),
        Category(name="Contract", description="Legal contracts and agreements"),
        Category(name="Letter", description="Correspondence and letters"),
        Category(name="Other", description="Other document types")
    ]

    # Classify and wait for completion
    result = client.classify_and_wait(
        file="document.pdf",
        categories=categories
    )

    print(f"Status: {result.status}")
    if result.result:
        print(f"Classification: {result.result.get('classification')}")
        print(f"Confidence: {result.result.get('confidence')}")


def simple_string_categories_example():
    """Classification using simple string categories."""
    print("\n=== Simple String Categories Example ===")

    # Using simple strings instead of Category objects
    categories = ["Invoice", "Receipt", "Contract", "Report", "Form"]

    result = client.classify_and_wait(
        file="document.pdf",
        categories=categories
    )

    if result.result:
        print(f"Document Type: {result.result.get('classification')}")
        print(f"Confidence Score: {result.result.get('confidence')}")


def financial_document_classification():
    """Classify financial documents."""
    print("\n=== Financial Document Classification ===")

    categories = [
        Category(
            name="Invoice",
            description="Invoices requesting payment for goods or services"
        ),
        Category(
            name="Receipt",
            description="Receipts confirming payment has been made"
        ),
        Category(
            name="Purchase Order",
            description="Purchase orders for requesting goods or services"
        ),
        Category(
            name="Bank Statement",
            description="Bank account statements showing transactions"
        ),
        Category(
            name="Tax Document",
            description="Tax forms, W-2s, 1099s, etc."
        )
    ]

    result = client.classify_and_wait(
        file="financial_doc.pdf",
        categories=categories
    )

    if result.result:
        print(f"Document Category: {result.result.get('classification')}")
        print(f"Confidence: {result.result.get('confidence')}")

        # Handle low confidence
        confidence = result.result.get('confidence', 0)
        if confidence < 0.7:
            print("Warning: Low confidence classification. Manual review recommended.")


def legal_document_classification():
    """Classify legal documents."""
    print("\n=== Legal Document Classification ===")

    categories = [
        Category(name="Contract", description="Legal contracts and agreements"),
        Category(name="NDA", description="Non-disclosure agreements"),
        Category(name="Power of Attorney", description="POA documents"),
        Category(name="Will", description="Last will and testament"),
        Category(name="Court Filing", description="Court documents and filings"),
        Category(name="Lease Agreement", description="Property lease agreements")
    ]

    result = client.classify_and_wait(
        file="legal_doc.pdf",
        categories=categories
    )

    if result.result:
        classification = result.result.get('classification')
        print(f"Legal Document Type: {classification}")

        # Get additional details if available
        if 'details' in result.result:
            print(f"Details: {result.result['details']}")


def async_classification_example():
    """Asynchronous classification example."""
    print("\n=== Async Classification Example ===")

    categories = ["Medical Record", "Lab Report", "Prescription", "Insurance Form"]

    # Start classification (non-blocking)
    response = client.classify(
        file="medical_doc.pdf",
        categories=categories
    )

    print(f"Job ID: {response.job_id}")
    print(f"Initial Status: {response.status}")

    # Later, check the result
    result = client.get_classify_result(job_id=response.job_id)

    print(f"Current Status: {result.status}")
    if result.status == "completed" and result.result:
        print(f"Classification: {result.result.get('classification')}")


def classify_from_url_example():
    """Classify document from URL."""
    print("\n=== Classify from URL Example ===")

    categories = [
        Category(name="Technical Spec", description="Technical specifications"),
        Category(name="User Manual", description="User guides and manuals"),
        Category(name="API Documentation", description="API reference docs"),
        Category(name="Tutorial", description="Tutorials and how-tos")
    ]

    result = client.classify_and_wait(
        file_url="https://example.com/document.pdf",
        categories=categories
    )

    if result.result:
        print(f"Document Type: {result.result.get('classification')}")


def batch_classification_example():
    """Classify multiple documents."""
    print("\n=== Batch Classification Example ===")

    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    categories = ["Invoice", "Receipt", "Contract", "Report"]

    results = []
    for file in files:
        try:
            result = client.classify_and_wait(
                file=file,
                categories=categories,
                max_wait=120.0  # 2 minutes per document
            )

            if result.result:
                results.append({
                    "file": file,
                    "classification": result.result.get('classification'),
                    "confidence": result.result.get('confidence')
                })
        except Exception as e:
            print(f"Error classifying {file}: {e}")

    # Display results
    print("\nBatch Classification Results:")
    for r in results:
        print(f"{r['file']}: {r['classification']} (confidence: {r['confidence']})")


if __name__ == "__main__":
    try:
        # Run examples
        # Note: Uncomment the examples you want to run

        # basic_classification_example()
        # simple_string_categories_example()
        # financial_document_classification()
        # legal_document_classification()
        # async_classification_example()
        # classify_from_url_example()
        # batch_classification_example()

        print("\nExamples completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
