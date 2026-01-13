"""Data models for the Unsiloed SDK."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Category:
    """Represents a classification or split category."""

    name: str
    description: Optional[str] = None


@dataclass
class ParseResponse:
    """Response from a parse operation."""

    job_id: str
    status: str
    file_name: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    message: Optional[str] = None
    credit_used: Optional[int] = None
    quota_remaining: Optional[int] = None
    total_chunks: Optional[int] = None
    chunks: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    merge_tables: Optional[bool] = None
    validate_table_segments: Optional[bool] = None
    keep_segment_types: Optional[str] = None


@dataclass
class ExtractResponse:
    """Response from an extract operation."""

    job_id: str
    status: str
    file_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    quota_remaining: Optional[int] = None


@dataclass
class ClassifyResponse:
    """Response from a classify operation."""

    job_id: str
    status: str
    progress: Optional[str] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    quota_remaining: Optional[int] = None


@dataclass
class SplitResponse:
    """Response from a split operation."""

    job_id: str
    status: str
    progress: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    quota_remaining: Optional[int] = None


@dataclass
class JobStatus:
    """Generic job status response."""

    job_id: str
    status: str
    progress: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
