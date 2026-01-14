"""Documentation query utilities.

Provides GPU documentation search and RAG query functions.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx

from wafer_core.telemetry.decorators import with_telemetry


@dataclass(frozen=True)
class DocsSearchResult:
    """Result from document search."""
    
    path: str
    content: str
    score: float
    url: str | None = None
    title: str | None = None


@dataclass(frozen=True)
class DocsSearchResponse:
    """Response from document search."""
    
    results: list[DocsSearchResult]
    query: str


@dataclass(frozen=True)
class DocsRAGChunk:
    """A chunk from streaming RAG response."""
    
    type: str  # "sources", "chunk", "done"
    text: str | None = None
    sources: list[dict[str, Any]] | None = None
    enriched_sources: list[dict[str, Any]] | None = None
    session_id: str | None = None
    metrics: dict[str, Any] | None = None


def _get_api_url() -> str:
    """Get the wafer-api base URL from environment or default."""
    return os.getenv("WAFER_DOCS_URL", "https://www.api.wafer.ai")


@with_telemetry("search_docs")
def search_docs(
    query: str,
    top_k: int = 5,
    max_chars_per_doc: int = 2000,
    api_url: str | None = None,
) -> DocsSearchResponse:
    """Search GPU documentation without LLM processing.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        max_chars_per_doc: Maximum characters per document
        api_url: Optional override for API URL (defaults to WAFER_DOCS_URL env var)
    
    Returns:
        DocsSearchResponse with search results
    
    Raises:
        RuntimeError: If HTTP request fails
    """
    base_url = api_url or _get_api_url()
    url = f"{base_url.rstrip('/')}/v1/docs/search"
    
    payload = {
        "query": query,
        "top_k": top_k,
        "max_chars_per_doc": max_chars_per_doc,
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            results = [
                DocsSearchResult(
                    path=r["path"],
                    content=r["content"],
                    score=r.get("score", 0.0),
                    url=r.get("url"),
                    title=r.get("title"),
                )
                for r in data.get("results", [])
            ]
            
            return DocsSearchResponse(
                results=results,
                query=data.get("query", query),
            )
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to search docs: {e}") from e


@with_telemetry("query_docs")
def query_docs(
    query: str,
    session_id: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    top_k: int = 5,
    max_chars_per_doc: int = 2000,
    api_url: str | None = None,
) -> list[DocsRAGChunk]:
    """Query GPU documentation with RAG (returns all chunks).
    
    Args:
        query: Question about GPU programming/documentation
        session_id: Optional session ID for follow-up questions (not yet used by API)
        conversation_history: Optional list of {"role": "user|assistant", "content": "..."}
        top_k: Number of documents to retrieve
        max_chars_per_doc: Maximum characters per document
        api_url: Optional override for API URL
    
    Returns:
        List of DocsRAGChunk events from the stream
    
    Raises:
        RuntimeError: If HTTP request fails
    """
    base_url = api_url or _get_api_url()
    url = f"{base_url.rstrip('/')}/v1/docs/rag/stream"
    
    payload: dict[str, Any] = {
        "query": query,
        "top_k": top_k,
        "max_chars_per_doc": max_chars_per_doc,
    }
    
    if conversation_history:
        payload["conversation_history"] = conversation_history
    
    chunks: list[DocsRAGChunk] = []
    
    try:
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    
                    try:
                        event_data = json.loads(line[6:])  # Skip "data: " prefix
                    except json.JSONDecodeError:
                        continue
                    
                    chunk = DocsRAGChunk(
                        type=event_data.get("type", ""),
                        text=event_data.get("text"),
                        sources=event_data.get("sources"),
                        enriched_sources=event_data.get("enriched_sources"),
                        session_id=event_data.get("session_id"),
                        metrics=event_data.get("metrics"),
                    )
                    chunks.append(chunk)
    
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to query docs: {e}") from e
    
    return chunks
