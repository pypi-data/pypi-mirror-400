"""
Router - Intent to Path routing.

The core of KmBiT: understanding WHAT you want and knowing WHERE it lives.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import re
from .fs import Path, AIFileSystem


@dataclass
class Route:
    """A routing rule: pattern → destination."""
    pattern: str           # Regex or keyword pattern
    destination: str       # Path in AI filesystem
    priority: int = 0      # Higher = checked first
    conditions: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._compiled = re.compile(self.pattern, re.IGNORECASE)

    def matches(self, query: str) -> bool:
        """Check if query matches this route."""
        return bool(self._compiled.search(query))


class Router:
    """
    The Router - maps intents to paths.

    Non-conversational. No reasoning.
    Just: query → pattern match → path.

    Like a network router: packet in, route lookup, forward.
    """

    def __init__(self, fs: Optional[AIFileSystem] = None):
        self.fs = fs or AIFileSystem()
        self.routes: List[Route] = []
        self._init_default_routes()

    def _init_default_routes(self):
        """Initialize default routing rules."""
        # Claude routes - complex reasoning, code
        self.add_route(Route(
            r"(review|analyze|refactor|debug|fix).*(code|bug|error)",
            "/agents/claude",
            priority=100,
        ))
        self.add_route(Route(
            r"(complex|difficult|hard|challenging)",
            "/agents/claude",
            priority=50,
        ))
        self.add_route(Route(
            r"(write|create|implement|build).*(function|class|module|api)",
            "/agents/claude",
            priority=90,
        ))
        self.add_route(Route(
            r"(explain|why|how does|reasoning)",
            "/agents/claude",
            priority=60,
        ))

        # Gemini routes - vision, research
        self.add_route(Route(
            r"(image|picture|photo|screenshot|diagram|visual)",
            "/agents/gemini",
            priority=100,
        ))
        self.add_route(Route(
            r"(research|search|find|look up|investigate)",
            "/agents/gemini",
            priority=80,
        ))
        self.add_route(Route(
            r"(draw|sketch|design|mockup|wireframe)",
            "/agents/gemini",
            priority=90,
        ))

        # Codex routes - research only
        self.add_route(Route(
            r"(summarize|summary|tldr|overview)",
            "/agents/codex",
            priority=70,
        ))
        self.add_route(Route(
            r"(compare|versus|vs|difference between)",
            "/agents/codex",
            priority=60,
        ))

        # Kit/Local routes - fast, cheap
        self.add_route(Route(
            r"(quick|fast|simple|basic|easy)",
            "/agents/kit",
            priority=80,
        ))
        self.add_route(Route(
            r"(validate|check|verify|confirm)",
            "/agents/kit",
            priority=70,
        ))
        self.add_route(Route(
            r"(translate|format|convert)",
            "/agents/kit",
            priority=60,
        ))

        # Sentinel routes - security
        self.add_route(Route(
            r"(safe|secure|trust|permission|allow)",
            "/agents/sentinel",
            priority=100,
        ))
        self.add_route(Route(
            r"(audit|log|trace|provenance)",
            "/agents/sentinel",
            priority=90,
        ))

        # Memory routes
        self.add_route(Route(
            r"(remember|memory|stored|saved|history)",
            "/memory/vector",
            priority=80,
        ))
        self.add_route(Route(
            r"(session|context|current|now)",
            "/memory/session",
            priority=70,
        ))
        self.add_route(Route(
            r"(relation|connect|link|graph)",
            "/memory/graph",
            priority=70,
        ))

        # Trust routes
        self.add_route(Route(
            r"(who did|who made|author|creator)",
            "/trust/actors",
            priority=80,
        ))
        self.add_route(Route(
            r"(what happened|action|event|did what)",
            "/trust/actions",
            priority=80,
        ))
        self.add_route(Route(
            r"(chain|provenance|history of|trace)",
            "/trust/chains",
            priority=80,
        ))

        # Sort by priority
        self.routes.sort(key=lambda r: -r.priority)

    def add_route(self, route: Route):
        """Add a routing rule."""
        self.routes.append(route)
        self.routes.sort(key=lambda r: -r.priority)

    def resolve(self, query: str) -> Optional[str]:
        """
        Resolve a query to a path.

        This is the core operation. Must be FAST.
        No LLM calls. No reasoning. Just pattern matching.
        """
        for route in self.routes:
            if route.matches(query):
                return route.destination

        # Default fallback
        return "/agents/kit"

    def which(self, query: str) -> Dict[str, Any]:
        """
        Like 'which' command - find where a query routes to.
        Returns full routing info.
        """
        path = self.resolve(query)
        node = self.fs.stat(path) if path else None

        matches = []
        for route in self.routes:
            if route.matches(query):
                matches.append({
                    "pattern": route.pattern,
                    "destination": route.destination,
                    "priority": route.priority,
                })

        return {
            "query": query,
            "resolved_path": path,
            "node": node,
            "matched_routes": matches,
        }

    def explain(self, query: str) -> str:
        """Explain routing decision."""
        info = self.which(query)
        lines = [f"Query: {query}", f"→ Routes to: {info['resolved_path']}", ""]

        if info['matched_routes']:
            lines.append("Matched patterns:")
            for m in info['matched_routes'][:3]:
                lines.append(f"  [{m['priority']}] {m['pattern']} → {m['destination']}")

        if info['node']:
            lines.append(f"\nCapabilities: {info['node'].get('metadata', {}).get('capabilities', [])}")

        return "\n".join(lines)
