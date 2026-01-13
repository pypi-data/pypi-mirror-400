"""Main async client for the Unsiloed SDK."""

import json
import asyncio
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import httpx

from .models import (
    ParseResponse,
    ExtractResponse,
    ClassifyResponse,
    SplitResponse,
    Category,
)
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    InvalidRequestError,
    APIError,
    TimeoutError,
    NotFoundError,
)


class AsyncUnsiloedClient:
    """
    Async client for interacting with the Unsiloed Vision API.

    Args:
        api_key: Your Unsiloed API key
        base_url: Base URL for the API (default: https://prod.visionapi.unsiloed.ai)
        timeout: Request timeout in seconds (default: 300)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://prod.visionapi.unsiloed.ai",
        timeout: float = 300.0,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "api-key": self.api_key,
        }

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"detail": response.text}

        if response.status_code == 401:
            raise AuthenticationError(
                data.get("detail", "Authentication failed"),
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code == 402:
            raise QuotaExceededError(
                data.get("detail", {}).get("message", "Quota exceeded"),
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code == 400:
            raise InvalidRequestError(
                data.get("detail", "Invalid request"),
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                data.get("detail", "Resource not found"),
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code == 408:
            raise TimeoutError(
                data.get("detail", "Request timeout"),
                status_code=response.status_code,
                response_data=data,
            )
        elif response.status_code >= 400:
            raise APIError(
                data.get("detail", f"API error: {response.status_code}"),
                status_code=response.status_code,
                response_data=data,
            )

        return data

    async def parse(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        url: Optional[str] = None,
        merge_tables: bool = False,
        enhanced_table: bool = False,
        validate_table_segments: bool = False,
        use_high_resolution: bool = False,
        segment_analysis: Optional[Dict[str, Any]] = None,
        error_handling: str = "Continue",
        segmentation_method: str = "smart_layout_detection",
        ocr_mode: str = "auto_ocr",
        ocr_engine: str = "UnsiloedHawk",
        expires_in: Optional[int] = None,
        llm_processing: Optional[Dict[str, Any]] = None,
        output_fields: Optional[Dict[str, Any]] = None,
        segment_type_naming: Optional[str] = None,
        keep_segment_types: str = "all",
    ) -> ParseResponse:
        """
        Parse a document to extract structured content (async).

        Args:
            file: Path to file or file bytes to parse
            url: URL of the document to process (alternative to file)
            merge_tables: Whether to merge consecutive table segments
            enhanced_table: Whether to use OpenAI for enhanced table processing
            validate_table_segments: Whether to validate table segments using VLM
            use_high_resolution: Enable high resolution processing
            segment_analysis: Segment analysis configuration
            error_handling: Error handling strategy (default: "Continue")
            segmentation_method: Segmentation strategy (default: "smart_layout_detection")
            ocr_mode: OCR strategy (default: "auto_ocr")
            ocr_engine: OCR engine to use (default: "UnsiloedHawk")
            expires_in: Expiration time in seconds
            llm_processing: LLM processing configuration
            output_fields: Output fields configuration
            segment_type_naming: Segment type naming configuration
            keep_segment_types: Comma-separated list of segment types to keep (default: "all")

        Returns:
            ParseResponse object with job_id and initial status
        """
        if not file and not url:
            raise InvalidRequestError("Either file or url must be provided")
        if file and url:
            raise InvalidRequestError("Provide either file or url, not both")

        files = {}
        data = {
            "merge_tables": str(merge_tables).lower(),
            "enhanced_table": str(enhanced_table).lower(),
            "validate_table_segments": str(validate_table_segments).lower(),
            "use_high_resolution": str(use_high_resolution).lower(),
            "error_handling": error_handling,
            "segmentation_method": segmentation_method,
            "ocr_mode": ocr_mode,
            "ocr_engine": ocr_engine,
            "keep_segment_types": keep_segment_types,
        }

        if url:
            data["url"] = url
        elif file:
            if isinstance(file, (str, Path)):
                file_path = Path(file)
                if not file_path.exists():
                    raise InvalidRequestError(f"File not found: {file}")
                files["file"] = open(file_path, "rb")
            elif isinstance(file, bytes):
                files["file"] = ("document.pdf", file)

        if segment_analysis:
            data["segment_analysis"] = json.dumps(segment_analysis)
        if expires_in:
            data["expires_in"] = str(expires_in)
        if llm_processing:
            data["llm_processing"] = json.dumps(llm_processing)
        if output_fields:
            data["output_fields"] = json.dumps(output_fields)
        if segment_type_naming:
            data["segment_type_naming"] = segment_type_naming

        try:
            response = await self._client.post(
                f"{self.base_url}/parse",
                headers=self._get_headers(),
                data=data,
                files=files if files else None,
            )
            result = self._handle_response(response)
            return ParseResponse(**result)
        finally:
            for f in files.values():
                if hasattr(f, "close"):
                    f.close()

    async def get_parse_result(
        self,
        job_id: str,
        enhanced_table: bool = False,
        keep_segment_types: Optional[str] = None,
        output_file: bool = False,
    ) -> ParseResponse:
        """
        Get the results of a parse job (async).

        Args:
            job_id: The job ID returned from parse()
            enhanced_table: Whether to use OpenAI for enhanced table processing
            keep_segment_types: Comma-separated list of segment types to keep
            output_file: Whether to return S3 URL instead of full output

        Returns:
            ParseResponse object with results when job is complete
        """
        headers = self._get_headers()
        if enhanced_table:
            headers["enhanced-table"] = "true"
        if keep_segment_types:
            headers["keep-segment-types"] = keep_segment_types
        if output_file:
            headers["output-file"] = "true"

        response = await self._client.get(
            f"{self.base_url}/parse/{job_id}",
            headers=headers,
        )
        result = self._handle_response(response)
        return ParseResponse(**result)

    async def parse_and_wait(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        url: Optional[str] = None,
        poll_interval: float = 2.0,
        max_wait: float = 600.0,
        **kwargs,
    ) -> ParseResponse:
        """
        Parse a document and wait for results (async polling).

        Args:
            file: Path to file or file bytes to parse
            url: URL of the document to process
            poll_interval: Seconds between status checks (default: 2.0)
            max_wait: Maximum seconds to wait (default: 600.0)
            **kwargs: Additional arguments passed to parse()

        Returns:
            ParseResponse object with complete results
        """
        response = await self.parse(file=file, url=url, **kwargs)
        job_id = response.job_id

        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            result = await self.get_parse_result(job_id)
            if result.status in ["Succeeded", "Failed", "completed", "failed"]:
                return result
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Parse job {job_id} did not complete within {max_wait} seconds")

    async def extract(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        file_url: Optional[str] = None,
        schema: Dict[str, Any] = None,
        citation_config: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.9,
    ) -> ExtractResponse:
        """Extract structured data from a document using a schema (async)."""
        if not file and not file_url:
            raise InvalidRequestError("Either file or file_url must be provided")
        if file and file_url:
            raise InvalidRequestError("Provide either file or file_url, not both")
        if not schema:
            raise InvalidRequestError("Schema is required")

        files = {}
        data = {
            "schema_data": json.dumps(schema),
            "citation_config": json.dumps(citation_config or {}),
            "confidence_threshold": confidence_threshold,
        }

        if file_url:
            data["file_url"] = file_url
        elif file:
            if isinstance(file, (str, Path)):
                file_path = Path(file)
                if not file_path.exists():
                    raise InvalidRequestError(f"File not found: {file}")
                files["pdf_file"] = open(file_path, "rb")
            elif isinstance(file, bytes):
                files["pdf_file"] = ("document.pdf", file)

        try:
            response = await self._client.post(
                f"{self.base_url}/extract",
                headers=self._get_headers(),
                data=data,
                files=files if files else None,
            )
            result = self._handle_response(response)
            return ExtractResponse(**result)
        finally:
            for f in files.values():
                if hasattr(f, "close"):
                    f.close()

    async def get_extract_result(self, job_id: str) -> ExtractResponse:
        """Get the results of an extraction job (async)."""
        response = await self._client.get(
            f"{self.base_url}/extract/{job_id}",
            headers=self._get_headers(),
        )
        result = self._handle_response(response)
        return ExtractResponse(**result)

    async def extract_and_wait(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        file_url: Optional[str] = None,
        schema: Dict[str, Any] = None,
        poll_interval: float = 2.0,
        max_wait: float = 600.0,
        **kwargs,
    ) -> ExtractResponse:
        """Extract data and wait for results (async polling)."""
        response = await self.extract(file=file, file_url=file_url, schema=schema, **kwargs)
        job_id = response.job_id

        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            result = await self.get_extract_result(job_id)
            if result.status in ["completed", "failed", "review"]:
                return result
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Extract job {job_id} did not complete within {max_wait} seconds")

    async def classify(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        file_url: Optional[str] = None,
        categories: List[Union[str, Category]] = None,
    ) -> ClassifyResponse:
        """Classify a document into predefined categories (async)."""
        if not file and not file_url:
            raise InvalidRequestError("Either file or file_url must be provided")
        if file and file_url:
            raise InvalidRequestError("Provide either file or file_url, not both")
        if not categories or len(categories) == 0:
            raise InvalidRequestError("At least one category is required")

        categories_data = []
        for cat in categories:
            if isinstance(cat, str):
                categories_data.append({"name": cat})
            elif isinstance(cat, Category):
                cat_dict = {"name": cat.name}
                if cat.description:
                    cat_dict["description"] = cat.description
                categories_data.append(cat_dict)
            elif isinstance(cat, dict):
                categories_data.append(cat)
            else:
                raise InvalidRequestError(f"Invalid category type: {type(cat)}")

        files = {}
        data = {
            "categories": json.dumps(categories_data),
        }

        if file_url:
            data["file_url"] = file_url
        elif file:
            if isinstance(file, (str, Path)):
                file_path = Path(file)
                if not file_path.exists():
                    raise InvalidRequestError(f"File not found: {file}")
                files["pdf_file"] = open(file_path, "rb")
            elif isinstance(file, bytes):
                files["pdf_file"] = ("document.pdf", file)

        try:
            response = await self._client.post(
                f"{self.base_url}/classify",
                headers=self._get_headers(),
                data=data,
                files=files if files else None,
            )
            result = self._handle_response(response)
            return ClassifyResponse(**result)
        finally:
            for f in files.values():
                if hasattr(f, "close"):
                    f.close()

    async def get_classify_result(self, job_id: str) -> ClassifyResponse:
        """Get the results of a classification job (async)."""
        response = await self._client.get(
            f"{self.base_url}/classify/{job_id}",
            headers=self._get_headers(),
        )
        result = self._handle_response(response)
        return ClassifyResponse(**result)

    async def classify_and_wait(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        file_url: Optional[str] = None,
        categories: List[Union[str, Category]] = None,
        poll_interval: float = 2.0,
        max_wait: float = 600.0,
    ) -> ClassifyResponse:
        """Classify a document and wait for results (async polling)."""
        response = await self.classify(file=file, file_url=file_url, categories=categories)
        job_id = response.job_id

        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            result = await self.get_classify_result(job_id)
            if result.status in ["completed", "failed"]:
                return result
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Classify job {job_id} did not complete within {max_wait} seconds")

    async def split(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        file_url: Optional[str] = None,
        categories: List[Union[str, Category]] = None,
    ) -> SplitResponse:
        """Split a document's pages into different categories (async)."""
        if not file and not file_url:
            raise InvalidRequestError("Either file or file_url must be provided")
        if file and file_url:
            raise InvalidRequestError("Provide either file or file_url, not both")
        if not categories or len(categories) == 0:
            raise InvalidRequestError("At least one category is required")

        categories_data = []
        for cat in categories:
            if isinstance(cat, str):
                categories_data.append({"name": cat})
            elif isinstance(cat, Category):
                cat_dict = {"name": cat.name}
                if cat.description:
                    cat_dict["description"] = cat.description
                categories_data.append(cat_dict)
            elif isinstance(cat, dict):
                categories_data.append(cat)
            else:
                raise InvalidRequestError(f"Invalid category type: {type(cat)}")

        files = {}
        data = {
            "categories": json.dumps(categories_data),
        }

        if file_url:
            data["file_url"] = file_url
        elif file:
            if isinstance(file, (str, Path)):
                file_path = Path(file)
                if not file_path.exists():
                    raise InvalidRequestError(f"File not found: {file}")
                if not file_path.name.lower().endswith(".pdf"):
                    raise InvalidRequestError("File must be a PDF")
                files["file"] = open(file_path, "rb")
            elif isinstance(file, bytes):
                files["file"] = ("document.pdf", file)

        try:
            response = await self._client.post(
                f"{self.base_url}/splitter",
                headers=self._get_headers(),
                data=data,
                files=files if files else None,
            )
            result = self._handle_response(response)
            return SplitResponse(**result)
        finally:
            for f in files.values():
                if hasattr(f, "close"):
                    f.close()

    async def get_split_result(self, job_id: str) -> SplitResponse:
        """Get the results of a split job (async)."""
        response = await self._client.get(
            f"{self.base_url}/splitter/{job_id}",
            headers=self._get_headers(),
        )
        result = self._handle_response(response)
        return SplitResponse(**result)

    async def split_and_wait(
        self,
        file: Optional[Union[str, Path, bytes]] = None,
        file_url: Optional[str] = None,
        categories: List[Union[str, Category]] = None,
        poll_interval: float = 2.0,
        max_wait: float = 1800.0,
    ) -> SplitResponse:
        """Split a document and wait for results (async polling)."""
        response = await self.split(file=file, file_url=file_url, categories=categories)
        job_id = response.job_id

        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            result = await self.get_split_result(job_id)
            if result.status in ["completed", "failed"]:
                return result
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Split job {job_id} did not complete within {max_wait} seconds")

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
