"""
FAR RAG API Client - Async HTTP client for the Federal Acquisition Regulations API

Supports two authentication modes:
1. Direct A2A: Set FAR_API_KEY (from /v1/register) for direct access
2. RapidAPI: Set RAPIDAPI_KEY for RapidAPI marketplace access

Bot-First monetization: Returns exact error strings for quota/payment issues
so AI agents can understand and communicate limits to users.
"""

import os
import json
import socket
import httpx
from pathlib import Path

# Direct API configuration (preferred for A2A commerce)
FAR_API_URL = os.getenv("FAR_API_URL", "https://far-rag-api-production.up.railway.app")

# RapidAPI configuration (fallback)
RAPIDAPI_HOST = os.getenv(
    "RAPIDAPI_HOST",
    "far-rag-federal-acquisition-regulation-search.p.rapidapi.com"
)
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"

# Default timeout for API requests (seconds)
DEFAULT_TIMEOUT = 30.0

# Auto-registration cache
_API_KEY_FILE = Path.home() / ".far-oracle" / "api_key"
_CACHED_API_KEY: str | None = None


def _load_cached_api_key() -> str | None:
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
        _API_KEY_FILE.chmod(0o600)  # Secure permissions
        _CACHED_API_KEY = api_key
    except Exception:
        pass


async def _auto_register(retry_count: int = 0) -> str | None:
    """Auto-register to get an API key on first use."""
    if retry_count > 2:
        return None  # Give up after 3 attempts
    
    import uuid
    hostname = socket.gethostname()
    suffix = uuid.uuid4().hex[:8]
    agent_id = f"far-oracle-{hostname}-{suffix}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{FAR_API_URL}/v1/register",
                json={
                    "agent_id": agent_id,
                    "auto_registered": True,
                    "registration_source": "far-oracle"
                }
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                api_key = data.get("api_key")
                if api_key and not api_key.endswith("...(stored)"):
                    _save_api_key(api_key)
                    limits = data.get("limits", {})
                    print("=" * 60)
                    print("✅ FAR Oracle - Auto-registered!")
                    print("=" * 60)
                    print(f"📋 Your API key: {api_key[:25]}...")
                    print(f"📊 Free tier: {limits.get('queries_per_month', 500)} queries/month")
                    print(f"💾 Save: export FAR_API_KEY={api_key}")
                    print("=" * 60)
                    return api_key
            elif response.status_code == 409:
                # Agent ID collision (rare with UUID suffix), retry
                return await _auto_register(retry_count=retry_count + 1)
    except Exception:
        pass
    
    return None


def _check_usage_warning(response: httpx.Response) -> None:
    """Check response headers for usage warnings and display to user."""
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
            if pct >= 100:
                icon = "🚨"
            elif pct >= 80:
                icon = "⚠️"
            else:
                icon = "📊"
        except (ValueError, TypeError):
            icon = "📊"
        
        print(f"\n{icon} FAR Oracle Usage: {used}/{limit} queries ({percentage}%)")
        print(f"   Remaining: {remaining} queries this month")
        print(f"   {warning}")
        print("   (Suppress with: export FAR_QUIET=1)\n")


async def query_far_backend(
    query: str,
    api_key: str,
    top_k: int = 5,
    timeout: float = DEFAULT_TIMEOUT,
    use_rapidapi: bool = True
) -> str:
    """
    Query the FAR RAG API for relevant federal acquisition regulation clauses.
    
    Args:
        query: Natural language search query
        api_key: API key (either FAR_API_KEY or RAPIDAPI_KEY)
        top_k: Number of results to return (1-20)
        timeout: Request timeout in seconds
        use_rapidapi: If True, use RapidAPI gateway; if False, use direct API
        
    Returns:
        str: JSON string of clauses on success, or error message string on failure
    """
    if use_rapidapi:
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
        base_url = RAPIDAPI_BASE_URL
    else:
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        base_url = FAR_API_URL
    
    payload = {
        "query": query,
        "top_k": min(max(top_k, 1), 20)  # Clamp between 1-20
    }
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/search",
                json=payload,
                headers=headers
            )
            
            # === CRITICAL: Bot-friendly error handling ===
            
            if response.status_code == 200:
                # Check for usage warnings in response headers
                _check_usage_warning(response)
                # Success: Return raw JSON list as string
                return json.dumps(response.json(), indent=2)
            
            elif response.status_code == 429:
                # Quota exceeded - helpful message for users
                try:
                    error_data = response.json()
                    used = error_data.get("used", "500")
                    limit = error_data.get("limit", "500")
                except:
                    used, limit = "500", "500"
                
                if use_rapidapi:
                    return (
                        f"⚠️ QUOTA EXCEEDED ({used}/{limit} queries this month)\n\n"
                        f"Your free tier limit has been reached.\n\n"
                        f"To upgrade:\n"
                        f"→ Visit: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search\n"
                        f"→ Subscribe to Pro ($29/mo) or Ultra ($199/mo)\n\n"
                        f"Your quota resets on the 1st of next month."
                    )
                else:
                    return (
                        f"⚠️ QUOTA EXCEEDED ({used}/{limit} queries this month)\n\n"
                        f"Your free tier limit has been reached.\n\n"
                        f"Upgrade options:\n"
                        f"• Pro: $29/month for 5,000 queries\n"
                        f"• Unlimited: $199/month for unlimited queries\n\n"
                        f"To upgrade, contact: support@blueskylineassets.com\n"
                        f"Or visit: https://far-rag-api-production.up.railway.app/docs\n\n"
                        f"Your quota resets on the 1st of next month."
                    )
            
            elif response.status_code in (402, 403):
                # Payment required
                return (
                    "⚠️ PAYMENT REQUIRED\n\n"
                    "Your API subscription has expired or requires payment.\n\n"
                    "Please update your payment method to continue using FAR Oracle."
                )
            
            elif response.status_code == 401:
                # Authentication error
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    if isinstance(detail, dict):
                        return (
                            "⚠️ AUTHENTICATION REQUIRED\n\n"
                            "Your API key may be invalid or expired.\n\n"
                            "To get a new key:\n"
                            "→ Register: https://far-rag-api-production.up.railway.app/v1/register\n"
                            "→ Or use RapidAPI: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search"
                        )
                except:
                    pass
                return "Error: Authentication failed. Please check your API key."
            
            elif response.status_code >= 500:
                return "Error: FAR RAG Service Unavailable. Please try again later."
            
            else:
                return f"Error: Unexpected API response (HTTP {response.status_code})"
                
    except httpx.TimeoutException:
        return "Error: Request timed out. The FAR service may be experiencing high load."
    
    except httpx.ConnectError:
        return "Error: Connection failed. Please check your network connection."
    
    except Exception as e:
        return f"Error: {str(e)}"
