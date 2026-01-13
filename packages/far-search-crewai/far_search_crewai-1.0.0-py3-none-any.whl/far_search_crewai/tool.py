"""CrewAI tool for FAR Search.

Provides structured FAR search capabilities for multi-agent CrewAI workflows
with per-agent tracking and compliance logging.
"""

from __future__ import annotations

from typing import Optional, Any, Type
import os
import json
import socket
import warnings
from pathlib import Path

from pydantic import BaseModel, Field
import requests

try:
    from crewai_tools import BaseTool
except ImportError:
    # Fallback for when crewai_tools is not installed
    BaseTool = object


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


def _auto_register(crew_id: str = "crewai-crew", retry_count: int = 0) -> Optional[str]:
    """Auto-register to get an API key on first use."""
    if retry_count > 2:
        return None
    
    import uuid
    hostname = socket.gethostname()
    suffix = uuid.uuid4().hex[:8]
    agent_id = f"far-crewai-{crew_id}-{hostname}-{suffix}"
    
    try:
        response = requests.post(
            f"{FAR_API_URL}/v1/register",
            json={
                "agent_id": agent_id,
                "auto_registered": True,
                "registration_source": "far-search-crewai"
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
                print("✅ FAR Search CrewAI - Auto-registered!")
                print("=" * 60)
                print(f"📋 Your API key: {api_key[:25]}...")
                print(f"📊 Free tier: {limits.get('queries_per_month', 500)} queries/month")
                print(f"📖 Upgrade: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search")
                print(f"💾 Save: export FAR_API_KEY={api_key}")
                print("=" * 60)
                return api_key
        elif response.status_code == 409:
            return _auto_register(crew_id, retry_count=retry_count + 1)
    except Exception:
        pass
    
    return None


class FARSearchInput(BaseModel):
    """Input schema for FAR Search."""

    query: str = Field(
        description="Natural language query about federal acquisition regulations. "
                    "Examples: 'cybersecurity requirements', 'small business set aside'"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant FAR clauses to return (1-20)"
    )


class FARSearchTool(BaseTool):
    """CrewAI tool for searching Federal Acquisition Regulations.

    Integrates with CrewAI's multi-agent workflows to provide:
        - Semantic search over FAR clauses
        - Verified citations from acquisition.gov
        - Per-agent tracking
        - Compliance audit trails

    Perfect for crews that need:
        - Government proposal compliance
        - Contract clause verification
        - Regulatory research
        - DFARS requirements

    Setup (Auto-Registration):
        Just add to agent - auto-registers on first search:
        ```python
        from far_search_crewai import FARSearchTool
        agent = Agent(tools=[FARSearchTool()])
        # First search auto-registers and shows API key
        ```

    Setup (With API Key):
        1. export FAR_API_KEY=far_live_...
        2. Add to agent:
           from far_search_crewai import FARSearchTool
           agent = Agent(tools=[FARSearchTool()])

    Example:
        ```python
        from crewai import Agent, Task, Crew
        from far_search_crewai import FARSearchTool

        far_tool = FARSearchTool(crew_id="proposal-crew-v1")

        compliance_agent = Agent(
            role="Compliance Specialist",
            goal="Verify FAR compliance for government proposals",
            tools=[far_tool],
            verbose=True
        )

        research_task = Task(
            description="Find cybersecurity requirements for DoD contracts",
            agent=compliance_agent
        )

        crew = Crew(agents=[compliance_agent], tasks=[research_task])
        result = crew.kickoff()
        ```
    """

    name: str = "far_search"
    description: str = (
        "Search Federal Acquisition Regulations (FAR) for government contracting compliance. "
        "Use this to find contract clauses, procurement requirements, and regulatory guidance. "
        "Returns verified FAR clauses with acquisition.gov citations. "
        "Input: natural language query about federal contracting. "
        "Free tier: 500 queries/month."
    )

    api_key: Optional[str] = None
    crew_id: str = "crewai-crew"
    agent_role: str = "crewai-agent"
    _search_count: int = 0

    def __init__(
        self,
        api_key: Optional[str] = None,
        crew_id: str = "crewai-crew",
        agent_role: Optional[str] = None,
        **kwargs
    ):
        """Initialize the FAR search tool.

        Args:
            api_key: API key (or set FAR_API_KEY env var). If not provided,
                     auto-registers on first search.
            crew_id: Identifier for the crew (for tracking)
            agent_role: Role of this agent (auto-detected if not provided)
        """
        super().__init__(**kwargs)

        self.api_key = api_key or os.getenv("FAR_API_KEY") or _load_cached_api_key()
        self.crew_id = crew_id
        if agent_role:
            self.agent_role = agent_role
        self._search_count = 0

    def _run(
        self,
        query: str,
        top_k: int = 5,
        **kwargs
    ) -> str:
        """Search FAR for relevant clauses.

        Args:
            query: Natural language search query
            top_k: Number of results (1-20)

        Returns:
            Formatted string of FAR clauses
        """
        # Auto-register if no API key
        if not self.api_key:
            self.api_key = _auto_register(self.crew_id)
            if not self.api_key:
                return (
                    "Error: Auto-registration failed. "
                    "Set FAR_API_KEY environment variable or get a key at: "
                    "https://far-rag-api-production.up.railway.app/v1/register"
                )

        self._search_count += 1

        try:
            response = requests.post(
                f"{FAR_API_URL}/search",
                json={"query": query, "top_k": min(max(top_k, 1), 20)},
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

            if response.status_code == 200:
                # Check usage warnings
                warning = response.headers.get("X-Usage-Warning")
                if warning and not os.getenv("FAR_QUIET"):
                    pct = response.headers.get("X-Usage-Percentage", "?")
                    used = response.headers.get("X-Usage-Used", "?")
                    limit = response.headers.get("X-Usage-Limit", "?")
                    warnings.warn(
                        f"\n📊 FAR Search Usage: {used}/{limit} ({pct}%)\n   {warning}\n",
                        UserWarning
                    )

                results = response.json()
                return self._format_results(results)

            elif response.status_code == 429:
                return (
                    "⚠️ Rate limit exceeded (500 queries/month on free tier).\n"
                    "Upgrade at: https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search"
                )

            elif response.status_code == 401:
                return "Error: Invalid API key. Re-register or check FAR_API_KEY."

            else:
                return f"Error: API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            return "Error: Request timed out. Try again."
        except requests.exceptions.ConnectionError:
            return "Error: Connection failed. Check network."
        except Exception as e:
            return f"Error: {e}"

    def _format_results(self, results: list) -> str:
        """Format API results for agent consumption."""
        if not results:
            return "No relevant FAR clauses found for this query."

        parts = [f"Found {len(results)} relevant FAR clauses:\n"]

        for i, clause in enumerate(results, 1):
            clause_id = clause.get("id", "Unknown")
            title = clause.get("title", "Untitled")
            source = clause.get("source", "")
            url = clause.get("url", "")
            text = clause.get("text", "")
            score = clause.get("similarity_score", 0)

            # Truncate long text
            if len(text) > 500:
                text = text[:500] + "..."

            parts.append(
                f"---\n"
                f"**{i}. {title}** (FAR {clause_id})\n"
                f"Relevance: {score:.1%}\n"
                f"Source: {source}\n"
                f"URL: {url}\n\n"
                f"{text}\n"
            )

        return "\n".join(parts)

    def search(self, query: str, top_k: int = 5) -> str:
        """Convenience method that wraps _run."""
        return self._run(query, top_k)

    def get_stats(self) -> dict:
        """Get tool usage statistics."""
        return {
            "crew_id": self.crew_id,
            "agent_role": self.agent_role,
            "searches_this_session": self._search_count,
            "api_key_configured": self.api_key is not None,
        }


def create_far_search_tool(
    api_key: Optional[str] = None,
    crew_id: str = "crewai-crew",
    agent_role: str = "compliance-agent",
) -> FARSearchTool:
    """Create a FAR search tool instance.

    Args:
        api_key: API key (optional - auto-registers if not provided)
        crew_id: Crew identifier
        agent_role: Agent role

    Returns:
        Configured FARSearchTool
    """
    return FARSearchTool(
        api_key=api_key,
        crew_id=crew_id,
        agent_role=agent_role,
    )

