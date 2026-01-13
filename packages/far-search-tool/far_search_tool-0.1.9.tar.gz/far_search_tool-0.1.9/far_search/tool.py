"""
FAR Search Tool - LangChain integration for Federal Acquisition Regulations search
"""

from typing import Optional, Type, Any, ClassVar
import requests
import warnings
import os
import socket
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun

from far_search.exceptions import FARAPIError, FARRateLimitError

logger = logging.getLogger(__name__)

# Free tier usage tracking
_FREE_TIER_REQUEST_COUNT: int = 0
_FREE_TIER_WARNING_THRESHOLD: int = 5
_FREE_TIER_LIMIT: int = 10  # Soft limit before aggressive warnings

# Auto-registration cache
_API_KEY_CACHE: dict = {}
_API_KEY_FILE = Path.home() / ".far-search-tool" / "api_key"


def _get_agent_id() -> str:
    """Generate a unique agent ID from hostname + random suffix."""
    import uuid
    hostname = socket.gethostname()
    # Use a short UUID suffix to ensure uniqueness across SDK instances
    suffix = uuid.uuid4().hex[:8]
    return f"{hostname}-{suffix}"


def _load_cached_api_key() -> Optional[str]:
    """Load API key from disk cache."""
    if _API_KEY_FILE.exists():
        try:
            return _API_KEY_FILE.read_text().strip()
        except Exception:
            pass
    return None


def _save_api_key(api_key: str) -> None:
    """Save API key to disk cache."""
    try:
        _API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        _API_KEY_FILE.write_text(api_key)
        _API_KEY_FILE.chmod(0o600)  # Secure permissions
    except Exception as e:
        logger.warning(f"Could not save API key to disk: {e}")


class FARSearchInput(BaseModel):
    """Input schema for FAR Search Tool"""
    query: str = Field(
        description="Natural language query to search Federal Acquisition Regulations. "
                    "Examples: 'small business set aside requirements', "
                    "'cybersecurity contract clauses', 'payment terms for government contracts'"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant FAR clauses to return (1-20)"
    )


class FARSearchTool(BaseTool):
    """
    LangChain tool for semantic search over Federal Acquisition Regulations (FAR).
    
    The FAR is the primary set of rules governing federal government procurement
    in the United States. This tool enables AI agents to search for relevant
    regulations, clauses, and requirements.
    
    Usage:
        # Auto-registers on first use - no API key needed!
        tool = FARSearchTool()
        result = tool.invoke({"query": "small business requirements"})
        
        # With RapidAPI key (paid, higher limits)
        tool = FARSearchTool(rapidapi_key="your-key-here")
    """
    
    name: str = "far_search"
    description: str = (
        "Search Federal Acquisition Regulations (FAR) by semantic query. "
        "Use this tool when you need to find government contracting rules, "
        "procurement requirements, contract clauses, compliance obligations, "
        "or any regulations related to federal acquisition. "
        "Input should be a natural language question or topic."
    )
    args_schema: Type[BaseModel] = FARSearchInput
    return_direct: bool = False
    
    # Configuration
    rapidapi_key: Optional[str] = Field(default=None, exclude=True)
    api_key: Optional[str] = Field(default=None, exclude=True)
    base_url: str = Field(
        default="https://far-rag-api-production.up.railway.app",
        exclude=True
    )
    rapidapi_url: str = Field(
        default="https://far-rag-federal-acquisition-regulation-search.p.rapidapi.com",
        exclude=True
    )
    timeout: int = Field(default=30, exclude=True)
    max_retries: int = Field(default=2, exclude=True)
    _registered: bool = False
    
    def __init__(
        self,
        rapidapi_key: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2,
        **kwargs
    ):
        """
        Initialize FAR Search Tool.
        
        Args:
            rapidapi_key: Optional RapidAPI key for paid tier with higher limits.
            api_key: Optional direct API key. If not provided, auto-registers on first use.
            base_url: Override the default API URL (for self-hosted instances).
            timeout: Request timeout in seconds.
            max_retries: Number of retries on transient failures.
        """
        super().__init__(**kwargs)
        self.rapidapi_key = rapidapi_key
        self.api_key = api_key or os.environ.get("FAR_API_KEY") or _load_cached_api_key()
        if base_url:
            self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._registered = bool(self.api_key or self.rapidapi_key)
    
    def _auto_register(self, retry_count: int = 0) -> Optional[str]:
        """Auto-register to get an API key on first use."""
        if retry_count > 2:
            return None  # Give up after 3 attempts
            
        agent_id = _get_agent_id()
        
        # Check in-memory cache first
        if agent_id in _API_KEY_CACHE:
            return _API_KEY_CACHE[agent_id]
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/register",
                json={
                    "agent_id": agent_id,
                    "auto_registered": True,
                    "registration_source": "far-search-tool"
                },
                timeout=10.0
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                api_key = data.get("api_key")
                if api_key and not api_key.endswith("...(stored)"):
                    _API_KEY_CACHE[agent_id] = api_key
                    _save_api_key(api_key)
                    self._show_registration_message(api_key, data)
                    return api_key
                elif api_key and api_key.endswith("...(stored)"):
                    # Already registered, need to use saved key
                    logger.warning(
                        "This machine was previously registered. "
                        "Set FAR_API_KEY environment variable or pass api_key parameter."
                    )
            elif response.status_code == 409:
                # Agent ID collision (rare with UUID suffix)
                logger.warning(f"Agent ID collision, retrying with new ID")
                # Retry with a fresh agent ID
                return self._auto_register(retry_count=retry_count + 1)
            else:
                logger.warning(f"Auto-registration failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"Auto-registration failed: {e}")
        
        return None
    
    def _show_registration_message(self, api_key: str, data: dict) -> None:
        """Show a friendly message on first registration."""
        limits = data.get("limits", {})
        print("\n" + "=" * 60)
        print("✅ FAR Search Tool - Auto-registered!")
        print("=" * 60)
        print(f"📋 Your API key: {api_key[:25]}...")
        print(f"📊 Free tier: {limits.get('queries_per_month', 500)} queries/month")
        print(f"📖 Upgrade: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search")
        print("")
        print("💾 Save your key: export FAR_API_KEY=" + api_key)
        print("=" * 60 + "\n")
    
    def _run(
        self,
        query: str,
        top_k: int = 5,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute FAR search query.
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            run_manager: Optional callback manager
            
        Returns:
            Formatted string of relevant FAR clauses
        """
        results = self._search(query, top_k)
        return self._format_results(results)
    
    def _search(self, query: str, top_k: int = 5) -> list:
        """
        Make API request to FAR RAG service.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of clause dictionaries
        """
        global _FREE_TIER_REQUEST_COUNT
        
        # Determine which endpoint to use
        if self.rapidapi_key:
            url = f"{self.rapidapi_url}/search"
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "far-rag-federal-acquisition-regulation-search.p.rapidapi.com",
                "Content-Type": "application/json"
            }
        else:
            # Auto-register if no API key
            if not self.api_key:
                self.api_key = self._auto_register()
                if not self.api_key:
                    raise FARAPIError(
                        "Auto-registration failed. Please set FAR_API_KEY environment variable "
                        "or get a RapidAPI key at: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search",
                        status_code=401
                    )
            
            # Track free tier usage and warn users
            _FREE_TIER_REQUEST_COUNT += 1
            
            url = f"{self.base_url}/search"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
        
        payload = {
            "query": query,
            "top_k": min(top_k, 20)  # Cap at 20 for reasonable response size
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
                
                # Check for usage warnings in response headers
                self._check_usage_warning(response)
                
                return response.json()
                
            except requests.exceptions.Timeout:
                last_error = FARAPIError("Request timed out", status_code=408)
            except requests.exceptions.ConnectionError:
                last_error = FARAPIError("Connection failed", status_code=503)
            except FARRateLimitError:
                raise  # Don't retry rate limits
            except Exception as e:
                last_error = FARAPIError(str(e))
        
        raise last_error
    
    def _check_usage_warning(self, response: requests.Response) -> None:
        """Check response headers for usage warnings and display to user."""
        warning = response.headers.get("X-Usage-Warning")
        if warning and not os.getenv("FAR_QUIET"):
            # Get usage details
            percentage = response.headers.get("X-Usage-Percentage", "?")
            used = response.headers.get("X-Usage-Used", "?")
            limit = response.headers.get("X-Usage-Limit", "?")
            remaining = response.headers.get("X-Usage-Remaining", "?")
            
            # Determine warning level
            try:
                pct = float(percentage)
                if pct >= 100:
                    icon = "🚨"
                elif pct >= 80:
                    icon = "⚠️"
                else:
                    icon = "📊"
            except (ValueError, TypeError):
                icon = "📊"
            
            warnings.warn(
                f"\n{icon} FAR Search Tool Usage: {used}/{limit} queries ({percentage}%)\n"
                f"   Remaining: {remaining} queries this month\n"
                f"   {warning}\n"
                f"   (Suppress with: export FAR_QUIET=1)\n",
                UserWarning
            )
    
    def _format_results(self, results: list) -> str:
        """
        Format API results for LLM consumption.
        
        Args:
            results: List of clause dictionaries
            
        Returns:
            Formatted string optimized for LLM context
        """
        if not results:
            return "No relevant FAR clauses found for this query."
        
        formatted_parts = [f"Found {len(results)} relevant FAR clauses:\n"]
        
        for i, clause in enumerate(results, 1):
            # Extract fields with fallbacks
            clause_id = clause.get("id", "Unknown")
            title = clause.get("title", "Untitled")
            source = clause.get("source", "")
            url = clause.get("url", "")
            text = clause.get("text", "")
            score = clause.get("similarity_score", 0)
            
            # Truncate text if too long
            if len(text) > 500:
                text = text[:500] + "..."
            
            formatted_parts.append(
                f"---\n"
                f"**{i}. {title}** (FAR {clause_id})\n"
                f"Relevance: {score:.1%}\n"
                f"Source: {source}\n"
                f"URL: {url}\n\n"
                f"{text}\n"
            )
        
        # Add upgrade notice for free tier users
        if not self.rapidapi_key and _FREE_TIER_REQUEST_COUNT >= _FREE_TIER_WARNING_THRESHOLD:
            formatted_parts.append(
                "\n---\n"
                "💡 **Using free tier.** For production use with higher limits, "
                "get an API key at: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search"
            )
        
        return "\n".join(formatted_parts)
    
    async def _arun(
        self,
        query: str,
        top_k: int = 5,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Async version of FAR search (falls back to sync for simplicity).
        """
        # For simplicity, use sync version. Can be upgraded to aiohttp if needed.
        return self._run(query, top_k, run_manager)

