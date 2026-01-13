"""
Quick test script for the Unsiloed SDK

Before running:
1. Set your API key: export UNSILOED_API_KEY="your-key-here"
2. Make sure you have httpx installed: pip install httpx

Run:
python test_sdk.py
"""

import os
import sys

# Add the SDK to the path so we can import it without installing
sys.path.insert(0, os.path.dirname(__file__))

def test_sync_client():
    """Test the synchronous client."""
    print("\n" + "="*50)
    print("Testing Synchronous Client")
    print("="*50)

    from unsiloed_sdk import UnsiloedClient

    api_key = os.getenv("UNSILOED_API_KEY")
    if not api_key:
        print("❌ Error: UNSILOED_API_KEY not set")
        print("Please run: export UNSILOED_API_KEY='your-key-here'")
        return False

    try:
        client = UnsiloedClient(api_key=api_key)
        print(f"✅ Client initialized successfully")
        print(f"   Base URL: {client.base_url}")
        print(f"   API Key: {api_key[:10]}...")

        # Test that we can start a parse job (but don't actually upload a file)
        print("\n📝 Client is ready to use!")
        print("\nExample usage:")
        print('  result = client.parse_and_wait(file="document.pdf")')

        client.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_async_client():
    """Test the async client."""
    print("\n" + "="*50)
    print("Testing Async Client")
    print("="*50)

    import asyncio
    from unsiloed_sdk import AsyncUnsiloedClient

    api_key = os.getenv("UNSILOED_API_KEY")
    if not api_key:
        print("❌ Error: UNSILOED_API_KEY not set")
        return False

    async def test():
        try:
            async with AsyncUnsiloedClient(api_key=api_key) as client:
                print(f"✅ Async client initialized successfully")
                print(f"   Base URL: {client.base_url}")
                print(f"   API Key: {api_key[:10]}...")

                print("\n📝 Async client is ready to use!")
                print("\nExample usage:")
                print('  result = await client.parse_and_wait(file="document.pdf")')
                return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    return asyncio.run(test())


def test_imports():
    """Test that all imports work."""
    print("\n" + "="*50)
    print("Testing Imports")
    print("="*50)

    try:
        from unsiloed_sdk import (
            UnsiloedClient,
            AsyncUnsiloedClient,
            Category,
            ParseResponse,
            ExtractResponse,
            ClassifyResponse,
            SplitResponse,
            AuthenticationError,
            QuotaExceededError,
        )
        print("✅ All imports successful!")
        print("\nAvailable classes:")
        print("  - UnsiloedClient (sync)")
        print("  - AsyncUnsiloedClient (async)")
        print("  - Category")
        print("  - ParseResponse, ExtractResponse, ClassifyResponse, SplitResponse")
        print("  - AuthenticationError, QuotaExceededError, etc.")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_with_real_file():
    """Test with an actual file (if provided)."""
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print("\n" + "="*50)
        print(f"Testing with file: {file_path}")
        print("="*50)

        from unsiloed_sdk import UnsiloedClient

        api_key = os.getenv("UNSILOED_API_KEY")
        if not api_key:
            print("❌ Error: UNSILOED_API_KEY not set")
            return False

        try:
            with UnsiloedClient(api_key=api_key) as client:
                print(f"Starting parse job for: {file_path}")
                response = client.parse(file=file_path)
                print(f"✅ Job started: {response.job_id}")
                print(f"   Status: {response.status}")
                print(f"   File: {response.file_name}")

                print("\nTo check status:")
                print(f'  result = client.get_parse_result("{response.job_id}")')
                return True

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run all tests."""
    print("🚀 Unsiloed SDK Test Suite")
    print()

    # Check for httpx
    try:
        import httpx
        print("✅ httpx is installed")
    except ImportError:
        print("❌ httpx is not installed")
        print("Please install it: pip install httpx")
        return

    # Run tests
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Sync Client", test_sync_client()))
    results.append(("Async Client", test_async_client()))

    # Optional: test with real file
    if len(sys.argv) > 1:
        results.append(("Real File Test", test_with_real_file()))

    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 All tests passed!")
        print("\nThe SDK is ready to use. Try:")
        print("  python test_sdk.py path/to/document.pdf")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
