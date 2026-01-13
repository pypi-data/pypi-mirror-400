"""
Unsiloed SDK - Python client for Unsiloed Vision API

This SDK provides both sync and async access to Unsiloed's document processing capabilities:
- Parse: Extract structured content from documents
- Extract: Extract specific data using schemas
- Classify: Classify documents into categories
- Split: Split documents by page categories

Choose the client that fits your application:
- UnsiloedClient: Synchronous client for simple scripts and traditional Python apps
- AsyncUnsiloedClient: Async client for FastAPI apps and concurrent processing
"""

from .sync_client import UnsiloedClient
from .client import AsyncUnsiloedClient
from .models import (
    ParseResponse,
    ExtractResponse,
    ClassifyResponse,
    SplitResponse,
    Category,
)
from .exceptions import (
    UnsiloedError,
    AuthenticationError,
    QuotaExceededError,
    InvalidRequestError,
    APIError,
)

__version__ = "0.1.0"
__all__ = [
    "UnsiloedClient",
    "AsyncUnsiloedClient",
    "ParseResponse",
    "ExtractResponse",
    "ClassifyResponse",
    "SplitResponse",
    "Category",
    "UnsiloedError",
    "AuthenticationError",
    "QuotaExceededError",
    "InvalidRequestError",
    "APIError",
]
