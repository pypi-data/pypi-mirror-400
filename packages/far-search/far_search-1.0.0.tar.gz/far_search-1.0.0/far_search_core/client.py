"""
FAR Search Core Client - Lightweight HTTP client for FAR RAG API.

No LangChain dependency - pure Python with requests only.
"""

import os
import json
import socket
import warnings
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import requests

from far_search_core.exceptions import FARAPIError, FARRateLimitError

# API Configuration
FAR_API_URL = "https://far-rag-api-production.up.railway.app"
RAPIDAPI_URL = "https://far-rag-federal-acquisition-regulation-search.p.rapidapi.com"
RAPIDAPI_HOST = "far-rag-federal-acquisition-regulation-search.p.rapidapi.com"

# Auto-registration cache
_API_KEY_FILE = Path.home() / ".far-search" / "api_key"
_CACHED_API_KEY: Optional[str] = None


@dataclass
class FARClause:
    """A Federal Acquisition Regulation clause."""
    id: str
    title: str
    text: str
    source: str
    url: str
    similarity_score: float
    
    @classmethod
    def from_dict(cls, data: dict) -> "FARClause":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            text=data.get("text", ""),
            source=data.get("source", ""),
            url=data.get("url", ""),
            similarity_score=data.get("similarity_score", 0.0),
        )


def _get_agent_id() -> str:
    """Generate a unique agent ID."""
    import uuid
    hostname = socket.gethostname()
    suffix = uuid.uuid4().hex[:8]
    return f"far-search-{hostname}-{suffix}"


def _load_cached_api_key() -> Optional[str]:
    """Load API key from disk cache."""
    global _CACHED_API_KEY
    if _CACHED_API_KEY:
        return _CACHED_API_KEY
    if _API_KEY_FILE.exists():
        try:
            _CACHED_API_KEY = _API_KEY_FILE.read_text().strip()
            return _CACHED_API_KEY
        except Exception:
            pass
    return None


def _save_api_key(api_key: str) -> None:
    """Save API key to disk cache."""
    global _CACHED_API_KEY
    try:
        _API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        _API_KEY_FILE.write_text(api_key)
        _API_KEY_FILE.chmod(0o600)
        _CACHED_API_KEY = api_key
    except Exception:
        pass


def _auto_register(retry_count: int = 0) -> Optional[str]:
    """Auto-register to get an API key on first use."""
    if retry_count > 2:
        return None
    
    agent_id = _get_agent_id()
    
    try:
        response = requests.post(
            f"{FAR_API_URL}/v1/register",
            json={
                "agent_id": agent_id,
                "auto_registered": True,
                "registration_source": "far-search"
            },
            timeout=10.0
        )
        
        if response.status_code in (200, 201):
            data = response.json()
            api_key = data.get("api_key")
            if api_key and not api_key.endswith("...(stored)"):
                _save_api_key(api_key)
                limits = data.get("limits", {})
                print("=" * 60)
                print("✅ FAR Search - Auto-registered!")
                print("=" * 60)
                print(f"📋 Your API key: {api_key[:25]}...")
                print(f"📊 Free tier: {limits.get('queries_per_month', 500)} queries/month")
                print(f"📖 Upgrade: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search")
                print(f"💾 Save: export FAR_API_KEY={api_key}")
                print("=" * 60)
                return api_key
        elif response.status_code == 409:
            return _auto_register(retry_count=retry_count + 1)
    except Exception:
        pass
    
    return None


def _check_usage_warning(response: requests.Response) -> None:
    """Check response headers for usage warnings."""
    if os.getenv("FAR_QUIET"):
        return
    
    warning = response.headers.get("X-Usage-Warning")
    if warning:
        percentage = response.headers.get("X-Usage-Percentage", "?")
        used = response.headers.get("X-Usage-Used", "?")
        limit = response.headers.get("X-Usage-Limit", "?")
        remaining = response.headers.get("X-Usage-Remaining", "?")
        
        try:
            pct = float(percentage)
            icon = "🚨" if pct >= 100 else "⚠️" if pct >= 80 else "📊"
        except (ValueError, TypeError):
            icon = "📊"
        
        warnings.warn(
            f"\n{icon} FAR Search Usage: {used}/{limit} queries ({percentage}%)\n"
            f"   Remaining: {remaining} queries this month\n"
            f"   {warning}\n"
            f"   (Suppress with: export FAR_QUIET=1)\n",
            UserWarning
        )


class FARSearchClient:
    """
    Lightweight client for FAR RAG API.
    
    No LangChain dependency - just requests.
    
    Usage:
        # Auto-registers on first use
        client = FARSearchClient()
        results = client.search("cybersecurity requirements")
        
        # With explicit API key
        client = FARSearchClient(api_key="far_live_...")
        
        # With RapidAPI key
        client = FARSearchClient(rapidapi_key="your-key")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rapidapi_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2,
    ):
        """
        Initialize FAR Search client.
        
        Args:
            api_key: Direct API key (from /v1/register). Auto-registers if not provided.
            rapidapi_key: RapidAPI key for paid tier.
            base_url: Override API URL (for self-hosted instances).
            timeout: Request timeout in seconds.
            max_retries: Number of retries on transient failures.
        """
        self.rapidapi_key = rapidapi_key
        self.api_key = api_key or os.getenv("FAR_API_KEY") or _load_cached_api_key()
        self.base_url = base_url or FAR_API_URL
        self.timeout = timeout
        self.max_retries = max_retries
    
    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[FARClause]:
        """
        Search Federal Acquisition Regulations.
        
        Args:
            query: Natural language search query.
            top_k: Number of results to return (1-20).
        
        Returns:
            List of FARClause objects.
        
        Raises:
            FARAPIError: If API returns an error.
            FARRateLimitError: If rate limit exceeded.
        """
        # Determine endpoint and headers
        if self.rapidapi_key:
            url = f"{RAPIDAPI_URL}/search"
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": RAPIDAPI_HOST,
                "Content-Type": "application/json"
            }
        else:
            # Auto-register if no API key
            if not self.api_key:
                self.api_key = _auto_register()
                if not self.api_key:
                    raise FARAPIError(
                        "Auto-registration failed. Set FAR_API_KEY or use rapidapi_key parameter.",
                        status_code=401
                    )
            
            url = f"{self.base_url}/search"
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
        
        payload = {
            "query": query,
            "top_k": min(max(top_k, 1), 20)
        }
        
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    raise FARRateLimitError()
                
                if response.status_code != 200:
                    raise FARAPIError(
                        f"API returned status {response.status_code}: {response.text}",
                        status_code=response.status_code
                    )
                
                # Check for usage warnings
                _check_usage_warning(response)
                
                # Parse results
                data = response.json()
                return [FARClause.from_dict(item) for item in data]
                
            except requests.exceptions.Timeout:
                last_error = FARAPIError("Request timed out", status_code=408)
            except requests.exceptions.ConnectionError:
                last_error = FARAPIError("Connection failed", status_code=503)
            except FARRateLimitError:
                raise
            except FARAPIError:
                raise
            except Exception as e:
                last_error = FARAPIError(str(e))
        
        raise last_error
    
    def search_text(self, query: str, top_k: int = 5) -> str:
        """
        Search and return formatted text (for LLM consumption).
        
        Args:
            query: Natural language search query.
            top_k: Number of results.
        
        Returns:
            Formatted string of results.
        """
        results = self.search(query, top_k)
        
        if not results:
            return "No relevant FAR clauses found for this query."
        
        parts = [f"Found {len(results)} relevant FAR clauses:\n"]
        
        for i, clause in enumerate(results, 1):
            text = clause.text[:500] + "..." if len(clause.text) > 500 else clause.text
            parts.append(
                f"---\n"
                f"**{i}. {clause.title}** (FAR {clause.id})\n"
                f"Relevance: {clause.similarity_score:.1%}\n"
                f"Source: {clause.source}\n"
                f"URL: {clause.url}\n\n"
                f"{text}\n"
            )
        
        return "\n".join(parts)
    
    def get_clause(self, clause_id: str) -> Optional[FARClause]:
        """
        Get a specific FAR clause by ID.
        
        Args:
            clause_id: Clause ID (e.g., "52.203-1").
        
        Returns:
            FARClause or None if not found.
        """
        if self.rapidapi_key:
            url = f"{RAPIDAPI_URL}/clause/{clause_id}"
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": RAPIDAPI_HOST,
            }
        else:
            if not self.api_key:
                self.api_key = _auto_register()
            url = f"{self.base_url}/clause/{clause_id}"
            headers = {"X-API-Key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return FARClause.from_dict(response.json())
            return None
        except Exception:
            return None


def search_far(query: str, top_k: int = 5, api_key: Optional[str] = None) -> List[FARClause]:
    """
    Convenience function to search FAR.
    
    Args:
        query: Natural language search query.
        top_k: Number of results.
        api_key: Optional API key.
    
    Returns:
        List of FARClause objects.
    
    Example:
        >>> from far_search_core import search_far
        >>> results = search_far("cybersecurity requirements")
        >>> for clause in results:
        ...     print(f"{clause.id}: {clause.title}")
    """
    client = FARSearchClient(api_key=api_key)
    return client.search(query, top_k)

