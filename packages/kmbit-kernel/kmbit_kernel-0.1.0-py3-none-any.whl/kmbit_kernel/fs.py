"""
AI Filesystem - Linux-style hierarchy for AI capabilities.

/agents     - Who can do what
/memory     - Where knowledge lives
/trust      - TIBET provenance chains
/intents    - Pattern matching rules
/routes     - Compiled routing table
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class NodeType(Enum):
    """Types of nodes in the AI filesystem."""
    ROOT = "root"
    DIRECTORY = "dir"
    AGENT = "agent"
    MEMORY = "memory"
    TRUST = "trust"
    INTENT = "intent"
    ROUTE = "route"


@dataclass
class Path:
    """A path in the AI filesystem."""
    parts: List[str]

    def __init__(self, path: str):
        path = path.strip("/")
        self.parts = path.split("/") if path else []

    def __str__(self) -> str:
        return "/" + "/".join(self.parts)

    def __truediv__(self, other: str) -> "Path":
        """Allow path / "subdir" syntax."""
        new_path = Path(str(self))
        new_path.parts.append(other)
        return new_path

    @property
    def parent(self) -> "Path":
        return Path("/".join(self.parts[:-1])) if self.parts else Path("/")

    @property
    def name(self) -> str:
        return self.parts[-1] if self.parts else ""


@dataclass
class Node:
    """A node in the AI filesystem."""
    name: str
    node_type: NodeType
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: Dict[str, "Node"] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.node_type.value,
            "metadata": self.metadata,
            "children": {k: v.to_dict() for k, v in self.children.items()}
        }


class AIFileSystem:
    """
    The AI Filesystem - indexes capabilities, not files.

    Standard hierarchy:
        /agents     - AI agents (claude, gemini, codex, kit, sentinel)
        /memory     - Knowledge stores (vector, graph, session)
        /trust      - TIBET chains (actors, actions)
        /intents    - Intent patterns
        /routes     - Routing rules
    """

    def __init__(self):
        self.root = Node("/", NodeType.ROOT)
        self._init_structure()

    def _init_structure(self):
        """Initialize the standard AI filesystem structure."""
        # /agents - Who can do what
        agents = Node("agents", NodeType.DIRECTORY)
        agents.children = {
            "claude": Node("claude", NodeType.AGENT, {
                "provider": "anthropic",
                "capabilities": ["reasoning", "code", "analysis", "complex"],
                "cost": "high",
                "latency": "medium",
            }),
            "gemini": Node("gemini", NodeType.AGENT, {
                "provider": "google",
                "capabilities": ["vision", "research", "multimodal", "diagrams"],
                "cost": "medium",
                "latency": "medium",
            }),
            "codex": Node("codex", NodeType.AGENT, {
                "provider": "openai",
                "capabilities": ["research", "analysis", "web"],
                "cost": "medium",
                "latency": "medium",
                "note": "research only, no code generation",
            }),
            "kit": Node("kit", NodeType.AGENT, {
                "provider": "local",
                "capabilities": ["inference", "validation", "fast"],
                "cost": "free",
                "latency": "low",
                "models": ["qwen2.5:3b", "qwen2.5:7b", "qwen2.5:32b"],
            }),
            "sentinel": Node("sentinel", NodeType.AGENT, {
                "provider": "local",
                "capabilities": ["validation", "security", "audit"],
                "cost": "free",
                "latency": "minimal",
            }),
        }
        self.root.children["agents"] = agents

        # /memory - Where knowledge lives
        memory = Node("memory", NodeType.DIRECTORY)
        memory.children = {
            "vector": Node("vector", NodeType.MEMORY, {"type": "embeddings"}),
            "graph": Node("graph", NodeType.MEMORY, {"type": "relations"}),
            "session": Node("session", NodeType.MEMORY, {"type": "temporary"}),
            "tibet": Node("tibet", NodeType.MEMORY, {"type": "provenance"}),
        }
        self.root.children["memory"] = memory

        # /trust - TIBET chains
        trust = Node("trust", NodeType.DIRECTORY)
        trust.children = {
            "actors": Node("actors", NodeType.TRUST, {"stores": "who"}),
            "actions": Node("actions", NodeType.TRUST, {"stores": "what"}),
            "chains": Node("chains", NodeType.TRUST, {"stores": "provenance"}),
        }
        self.root.children["trust"] = trust

        # /intents - Pattern matching
        intents = Node("intents", NodeType.DIRECTORY)
        self.root.children["intents"] = intents

        # /routes - Compiled routing table
        routes = Node("routes", NodeType.DIRECTORY)
        self.root.children["routes"] = routes

    def resolve(self, path: str | Path) -> Optional[Node]:
        """Resolve a path to a node."""
        if isinstance(path, str):
            path = Path(path)

        current = self.root
        for part in path.parts:
            if part in current.children:
                current = current.children[part]
            else:
                return None
        return current

    def ls(self, path: str = "/") -> List[str]:
        """List contents of a directory."""
        node = self.resolve(path)
        if node and node.children:
            return list(node.children.keys())
        return []

    def stat(self, path: str) -> Optional[Dict]:
        """Get metadata for a path."""
        node = self.resolve(path)
        if node:
            return {
                "name": node.name,
                "type": node.node_type.value,
                "metadata": node.metadata,
                "children": len(node.children),
            }
        return None

    def mount(self, path: str, node: Node):
        """Mount a node at a path."""
        p = Path(path)
        parent = self.resolve(p.parent)
        if parent:
            parent.children[p.name] = node

    def tree(self, path: str = "/", indent: int = 0) -> str:
        """Print a tree view."""
        node = self.resolve(path)
        if not node:
            return ""

        lines = []
        prefix = "  " * indent
        lines.append(f"{prefix}{node.name}/" if node.children else f"{prefix}{node.name}")

        for child in node.children.values():
            child_path = f"{path}/{child.name}".replace("//", "/")
            lines.append(self.tree(child_path, indent + 1))

        return "\n".join(lines)
