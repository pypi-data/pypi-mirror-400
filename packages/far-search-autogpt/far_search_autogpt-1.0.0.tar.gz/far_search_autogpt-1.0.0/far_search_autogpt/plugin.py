"""AutoGPT plugin for FAR Search.

This plugin integrates with AutoGPT to provide Federal Acquisition Regulations
search capabilities directly within agent workflows.

Setup (Auto-Registration):
    1. pip install far-search-autogpt
    2. Add to AutoGPT plugins
    3. First search auto-registers and displays your API key

Setup (With API Key):
    1. pip install far-search-autogpt
    2. export FAR_API_KEY=far_live_...
    3. Add to AutoGPT plugins
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
import os
import json
import socket
import warnings
from pathlib import Path

import requests


# API Configuration
FAR_API_URL = "https://far-rag-api-production.up.railway.app"

# Auto-registration cache
_API_KEY_FILE = Path.home() / ".far-search" / "api_key"
_CACHED_API_KEY: Optional[str] = None


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
    
    import uuid
    hostname = socket.gethostname()
    suffix = uuid.uuid4().hex[:8]
    agent_id = f"far-autogpt-{hostname}-{suffix}"
    
    try:
        response = requests.post(
            f"{FAR_API_URL}/v1/register",
            json={
                "agent_id": agent_id,
                "auto_registered": True,
                "registration_source": "far-search-autogpt"
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
                print("✅ FAR Search AutoGPT - Auto-registered!")
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


class FARSearchPlugin:
    """AutoGPT plugin for searching Federal Acquisition Regulations.

    Provides commands for:
        - Semantic search over FAR clauses
        - Getting specific clauses by ID
        - Verifying FAR citations from AI responses

    Use Cases:
        - Government contract proposal writing
        - Compliance verification
        - Regulatory research

    Setup:
        1. Install: pip install far-search-autogpt
        2. Get API key (or auto-register on first use):
           curl -X POST https://far-rag-api-production.up.railway.app/v1/register \\
             -d '{"agent_id":"my-autogpt"}'
        3. Set FAR_API_KEY environment variable
        4. Enable in AutoGPT plugins configuration
    """

    def __init__(self):
        """Initialize the plugin."""
        self.name = "far-search"
        self.version = "1.0.0"
        self.description = "Search Federal Acquisition Regulations (FAR) for government contracting compliance"

        self._api_key: Optional[str] = os.getenv("FAR_API_KEY") or _load_cached_api_key()
        self._search_count: int = 0

    def can_handle_post_prompt(self) -> bool:
        """Plugin can handle post-prompt processing."""
        return True

    def post_prompt(self, prompt: str) -> str:
        """No modification to prompt."""
        return prompt

    def can_handle_on_response(self) -> bool:
        """Plugin can handle agent responses."""
        return False

    def can_handle_pre_command(self) -> bool:
        """Plugin can handle pre-command events."""
        return False

    def can_handle_post_command(self) -> bool:
        """Plugin can handle post-command events."""
        return False

    def can_handle_chat_completion(
        self,
        messages: list,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> bool:
        """Plugin cannot handle chat completions directly."""
        return False

    def search_far(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """
        Search Federal Acquisition Regulations.

        This command searches the FAR database for relevant clauses based on
        your natural language query.

        Args:
            query: Natural language search query
                   Examples: "cybersecurity requirements", "small business set aside"
            top_k: Number of results to return (1-20)

        Returns:
            JSON string with relevant FAR clauses
        """
        # Auto-register if no API key
        if not self._api_key:
            self._api_key = _auto_register()
            if not self._api_key:
                return json.dumps({
                    "error": "Auto-registration failed",
                    "action": "Set FAR_API_KEY environment variable",
                    "register_url": f"{FAR_API_URL}/v1/register"
                })

        self._search_count += 1

        try:
            response = requests.post(
                f"{FAR_API_URL}/search",
                json={"query": query, "top_k": min(max(top_k, 1), 20)},
                headers={
                    "X-API-Key": self._api_key,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                # Check usage warnings
                warning = response.headers.get("X-Usage-Warning")
                if warning and not os.getenv("FAR_QUIET"):
                    pct = response.headers.get("X-Usage-Percentage", "?")
                    print(f"[FAR Search] Usage: {pct}% - {warning}")

                return json.dumps(response.json(), indent=2)

            elif response.status_code == 429:
                return json.dumps({
                    "error": "Rate limit exceeded",
                    "message": "Free tier limit reached (500 queries/month)",
                    "upgrade_url": "https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search"
                })

            elif response.status_code == 401:
                return json.dumps({
                    "error": "Authentication failed",
                    "action": "Check your FAR_API_KEY",
                    "register_url": f"{FAR_API_URL}/v1/register"
                })

            else:
                return json.dumps({
                    "error": f"API error: HTTP {response.status_code}",
                    "details": response.text[:200]
                })

        except requests.exceptions.Timeout:
            return json.dumps({"error": "Request timed out"})
        except requests.exceptions.ConnectionError:
            return json.dumps({"error": "Connection failed"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_far_clause(self, clause_id: str) -> str:
        """
        Get a specific FAR clause by ID.

        Args:
            clause_id: The FAR clause ID (e.g., "52.203-1", "52.204-2")

        Returns:
            JSON string with the clause details
        """
        if not self._api_key:
            self._api_key = _auto_register()
            if not self._api_key:
                return json.dumps({"error": "No API key configured"})

        try:
            response = requests.get(
                f"{FAR_API_URL}/clause/{clause_id}",
                headers={"X-API-Key": self._api_key},
                timeout=30.0
            )

            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            elif response.status_code == 404:
                return json.dumps({"error": f"Clause {clause_id} not found"})
            else:
                return json.dumps({"error": f"API error: HTTP {response.status_code}"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_search_stats(self) -> Dict[str, Any]:
        """Get plugin usage statistics.

        Returns:
            Dict with search count and API key status
        """
        return {
            "searches_this_session": self._search_count,
            "api_key_configured": self._api_key is not None,
            "api_key_prefix": self._api_key[:16] + "..." if self._api_key else None,
        }


def init_plugin() -> FARSearchPlugin:
    """Initialize and return the plugin instance.

    This function is called by AutoGPT's plugin loader.

    Returns:
        Configured plugin instance
    """
    return FARSearchPlugin()

