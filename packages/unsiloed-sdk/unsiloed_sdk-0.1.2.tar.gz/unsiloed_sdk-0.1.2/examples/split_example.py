"""
Example: Document Splitting with Unsiloed SDK

This example demonstrates how to split document pages into different categories.
"""

import os
from unsiloed_sdk import UnsiloedClient, Category

# Initialize the client
API_KEY = os.getenv("UNSILOED_API_KEY", "your-api-key-here")
client = UnsiloedClient(api_key=API_KEY)


def basic_split_example():
    """Basic document splitting example."""
    print("\n=== Basic Split Example ===")

    # Define categories for splitting
    categories = [
        Category(name="Cover Page", description="Document cover and title pages"),
        Category(name="Table of Contents", description="TOC pages"),
        Category(name="Main Content", description="Primary document content"),
        Category(name="Appendix", description="Supplementary materials and appendices")
    ]

    # Split and wait for completion
    result = client.split_and_wait(
        file="report.pdf",
        categories=categories,
        max_wait=1800.0  # 30 minutes max
    )

    print(f"Status: {result.status}")
    if result.result:
        splits = result.result.get('splits', {})
        print("\nPage Distribution:")
        for category, pages in splits.items():
            print(f"{category}: {len(pages)} pages - {pages}")


def simple_section_split():
    """Split document into simple sections."""
    print("\n=== Simple Section Split ===")

    # Using simple string categories
    categories = ["Introduction", "Methodology", "Results", "Discussion", "Conclusion"]

    result = client.split_and_wait(
        file="research_paper.pdf",
        categories=categories
    )

    if result.result:
        print("\nSections Found:")
        for section, pages in result.result.get('splits', {}).items():
            print(f"  {section}: Pages {pages}")


def book_chapter_split():
    """Split a book into chapters."""
    print("\n=== Book Chapter Split ===")

    categories = [
        Category(name="Front Matter", description="Title page, copyright, preface, TOC"),
        Category(name="Chapter 1", description="First chapter content"),
        Category(name="Chapter 2", description="Second chapter content"),
        Category(name="Chapter 3", description="Third chapter content"),
        Category(name="References", description="Bibliography and references"),
        Category(name="Index", description="Book index")
    ]

    result = client.split_and_wait(
        file="book.pdf",
        categories=categories,
        max_wait=3600.0  # 1 hour for large books
    )

    if result.result:
        splits = result.result.get('splits', {})

        print("\nBook Structure:")
        total_pages = 0
        for section, pages in splits.items():
            page_count = len(pages)
            total_pages += page_count
            print(f"{section}: {page_count} pages")

        print(f"\nTotal Pages: {total_pages}")


def contract_section_split():
    """Split a contract into sections."""
    print("\n=== Contract Section Split ===")

    categories = [
        Category(name="Header", description="Contract title and parties"),
        Category(name="Definitions", description="Definitions and terms"),
        Category(name="Terms & Conditions", description="Main terms and conditions"),
        Category(name="Payment Terms", description="Payment clauses"),
        Category(name="Termination", description="Termination clauses"),
        Category(name="Signatures", description="Signature pages")
    ]

    result = client.split_and_wait(
        file="contract.pdf",
        categories=categories
    )

    if result.result:
        print("\nContract Sections:")
        for section, pages in result.result.get('splits', {}).items():
            print(f"{section}: Pages {pages}")


def async_split_example():
    """Asynchronous splitting example."""
    print("\n=== Async Split Example ===")

    categories = [
        "Executive Summary",
        "Financial Overview",
        "Market Analysis",
        "Projections",
        "Appendices"
    ]

    # Start split operation (non-blocking)
    response = client.split(
        file="business_plan.pdf",
        categories=categories
    )

    print(f"Job ID: {response.job_id}")
    print(f"Initial Status: {response.status}")

    # Later, check the result
    result = client.get_split_result(job_id=response.job_id)

    print(f"Current Status: {result.status}")
    print(f"Progress: {result.progress}")

    if result.status == "completed" and result.result:
        print("\nSplit Results:")
        for section, pages in result.result.get('splits', {}).items():
            print(f"{section}: {pages}")


def split_from_url_example():
    """Split document from URL."""
    print("\n=== Split from URL Example ===")

    categories = [
        Category(name="Title Page"),
        Category(name="Abstract"),
        Category(name="Body"),
        Category(name="References")
    ]

    result = client.split_and_wait(
        file_url="https://example.com/paper.pdf",
        categories=categories
    )

    if result.result:
        print("\nDocument Structure:")
        for section, pages in result.result.get('splits', {}).items():
            print(f"{section}: {pages}")


def form_section_split():
    """Split a multi-part form."""
    print("\n=== Form Section Split ===")

    categories = [
        Category(name="Personal Information", description="Name, address, contact info"),
        Category(name="Employment History", description="Work experience section"),
        Category(name="Education", description="Educational background"),
        Category(name="References", description="Professional references"),
        Category(name="Declarations", description="Declarations and signatures")
    ]

    result = client.split_and_wait(
        file="application_form.pdf",
        categories=categories
    )

    if result.result:
        splits = result.result.get('splits', {})

        print("\nForm Sections:")
        for section, pages in splits.items():
            if pages:
                print(f"✓ {section}: Page(s) {pages}")
            else:
                print(f"✗ {section}: Not found")


def medical_record_split():
    """Split medical records into sections."""
    print("\n=== Medical Record Split ===")

    categories = [
        Category(name="Patient Info", description="Patient demographics and information"),
        Category(name="Medical History", description="Patient medical history"),
        Category(name="Lab Results", description="Laboratory test results"),
        Category(name="Imaging", description="Radiology and imaging reports"),
        Category(name="Prescriptions", description="Medication prescriptions"),
        Category(name="Progress Notes", description="Clinical progress notes")
    ]

    result = client.split_and_wait(
        file="medical_record.pdf",
        categories=categories
    )

    if result.result:
        print("\nMedical Record Structure:")
        for section, pages in result.result.get('splits', {}).items():
            print(f"{section}: Pages {pages}")


if __name__ == "__main__":
    try:
        # Run examples
        # Note: Uncomment the examples you want to run

        # basic_split_example()
        # simple_section_split()
        # book_chapter_split()
        # contract_section_split()
        # async_split_example()
        # split_from_url_example()
        # form_section_split()
        # medical_record_split()

        print("\nExamples completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
