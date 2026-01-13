"""
KmBiT Kernel - The core.

Non-conversational. No chat. Just routing and indexing.
Like a CPU: silent, fast, always working.

This is the operating system for AI agents.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

from .fs import AIFileSystem, Path, Node, NodeType
from .router import Router, Route
from .index import Index


@dataclass
class KernelStats:
    """Kernel statistics."""
    queries: int = 0
    routes_resolved: int = 0
    index_lookups: int = 0
    avg_resolve_time_ms: float = 0.0
    uptime_seconds: float = 0.0


class Kernel:
    """
    The KmBiT Kernel.

    Like a Unix kernel:
        - Manages the AI filesystem
        - Routes queries to agents
        - Maintains the knowledge index
        - No conversation, no reasoning

    Usage:
        kernel = Kernel()
        path = kernel.resolve("review this code")
        # Returns: "/agents/claude"
    """

    def __init__(self, index_path: Optional[str] = None):
        self.fs = AIFileSystem()
        self.router = Router(self.fs)
        self.index = Index(index_path)
        self._stats = KernelStats()
        self._start_time = time.time()

    # =========================================
    # Core operations - MUST BE FAST
    # =========================================

    def resolve(self, query: str) -> str:
        """
        Resolve a query to a path.

        This is THE core operation. Must complete in < 10ms.
        No LLM calls. No external requests. Pure routing.
        """
        start = time.time()

        # Try router first (pattern matching)
        path = self.router.resolve(query)

        # Update stats
        self._stats.queries += 1
        self._stats.routes_resolved += 1
        elapsed_ms = (time.time() - start) * 1000
        self._update_avg_time(elapsed_ms)

        return path

    def which(self, query: str) -> Dict[str, Any]:
        """Like 'which' command - explain where a query routes."""
        return self.router.which(query)

    def lookup(self, key: str) -> Optional[str]:
        """Index lookup by key."""
        self._stats.index_lookups += 1
        return self.index.lookup(key)

    # =========================================
    # Filesystem operations
    # =========================================

    def ls(self, path: str = "/") -> List[str]:
        """List contents of a path."""
        return self.fs.ls(path)

    def stat(self, path: str) -> Optional[Dict]:
        """Get metadata for a path."""
        return self.fs.stat(path)

    def tree(self, path: str = "/") -> str:
        """Print tree view."""
        return self.fs.tree(path)

    def mount(self, path: str, agent_name: str, metadata: Dict = None):
        """Mount a new agent at a path."""
        node = Node(agent_name, NodeType.AGENT, metadata or {})
        self.fs.mount(path, node)

    # =========================================
    # Routing operations
    # =========================================

    def add_route(self, pattern: str, destination: str, priority: int = 50):
        """Add a custom route."""
        self.router.add_route(Route(pattern, destination, priority))

    def routes(self) -> List[Dict]:
        """List all routes."""
        return [
            {"pattern": r.pattern, "destination": r.destination, "priority": r.priority}
            for r in self.router.routes
        ]

    # =========================================
    # Index operations
    # =========================================

    def index_add(self, key: str, path: str, metadata: Dict = None, tags: set = None):
        """Add to the knowledge index."""
        self.index.index(key, path, metadata, tags)

    def index_search(self, pattern: str) -> List[str]:
        """Search the index."""
        return self.index.search(pattern)

    def index_stats(self) -> Dict[str, int]:
        """Index statistics."""
        return self.index.stats()

    # =========================================
    # Kernel stats
    # =========================================

    def stats(self) -> Dict[str, Any]:
        """Get kernel statistics."""
        self._stats.uptime_seconds = time.time() - self._start_time
        return {
            "queries": self._stats.queries,
            "routes_resolved": self._stats.routes_resolved,
            "index_lookups": self._stats.index_lookups,
            "avg_resolve_time_ms": round(self._stats.avg_resolve_time_ms, 3),
            "uptime_seconds": round(self._stats.uptime_seconds, 1),
        }

    def _update_avg_time(self, elapsed_ms: float):
        """Update running average of resolve time."""
        n = self._stats.queries
        if n == 1:
            self._stats.avg_resolve_time_ms = elapsed_ms
        else:
            # Running average
            self._stats.avg_resolve_time_ms = (
                self._stats.avg_resolve_time_ms * (n - 1) + elapsed_ms
            ) / n

    # =========================================
    # CLI-style interface
    # =========================================

    def execute(self, command: str) -> str:
        """
        Execute a kernel command.

        Commands:
            which <query>     - Show routing for query
            ls [path]         - List path contents
            stat <path>       - Show path metadata
            tree [path]       - Show tree view
            stats             - Show kernel stats
            routes            - List all routes
        """
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "which":
            return self.router.explain(args)
        elif cmd == "ls":
            return "\n".join(self.ls(args or "/"))
        elif cmd == "stat":
            stat = self.stat(args)
            return str(stat) if stat else f"Not found: {args}"
        elif cmd == "tree":
            return self.tree(args or "/")
        elif cmd == "stats":
            return str(self.stats())
        elif cmd == "routes":
            return "\n".join(
                f"[{r['priority']}] {r['pattern']} → {r['destination']}"
                for r in self.routes()[:20]
            )
        else:
            return f"Unknown command: {cmd}"


# Singleton kernel instance
_kernel: Optional[Kernel] = None


def get_kernel() -> Kernel:
    """Get the global kernel instance."""
    global _kernel
    if _kernel is None:
        _kernel = Kernel()
    return _kernel
