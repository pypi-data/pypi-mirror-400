"""
Index - The knowledge index.

Fast lookups. No reasoning. Pure indexing.
Like an inode table, but for AI knowledge.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
import hashlib
import json
from pathlib import Path as FilePath


@dataclass
class IndexEntry:
    """An entry in the index."""
    key: str
    path: str
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)


class Index:
    """
    The Knowledge Index.

    Fast key → path lookups.
    Like a database index, but for AI capabilities.

    Operations:
        - index(key, path)    : Add to index
        - lookup(key)         : Find path for key
        - search(pattern)     : Find matching keys
        - tags(tag)           : Find by tag
    """

    def __init__(self, persist_path: Optional[str] = None):
        self._entries: Dict[str, IndexEntry] = {}
        self._by_tag: Dict[str, Set[str]] = {}
        self._by_path: Dict[str, Set[str]] = {}
        self.persist_path = persist_path

        if persist_path and FilePath(persist_path).exists():
            self._load()

    def index(self, key: str, path: str, metadata: Dict = None, tags: Set[str] = None):
        """Add or update an index entry."""
        checksum = hashlib.md5(f"{key}:{path}".encode()).hexdigest()[:8]

        entry = IndexEntry(
            key=key,
            path=path,
            checksum=checksum,
            metadata=metadata or {},
            tags=tags or set(),
        )

        self._entries[key] = entry

        # Update tag index
        for tag in entry.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = set()
            self._by_tag[tag].add(key)

        # Update path index
        if path not in self._by_path:
            self._by_path[path] = set()
        self._by_path[path].add(key)

    def lookup(self, key: str) -> Optional[str]:
        """Fast key → path lookup."""
        entry = self._entries.get(key)
        return entry.path if entry else None

    def get(self, key: str) -> Optional[IndexEntry]:
        """Get full entry."""
        return self._entries.get(key)

    def search(self, pattern: str) -> List[str]:
        """Search keys by pattern."""
        pattern = pattern.lower()
        return [k for k in self._entries.keys() if pattern in k.lower()]

    def by_tag(self, tag: str) -> List[str]:
        """Find all keys with a tag."""
        return list(self._by_tag.get(tag, set()))

    def by_path(self, path: str) -> List[str]:
        """Find all keys pointing to a path."""
        return list(self._by_path.get(path, set()))

    def stats(self) -> Dict[str, int]:
        """Index statistics."""
        return {
            "entries": len(self._entries),
            "tags": len(self._by_tag),
            "paths": len(self._by_path),
        }

    def _save(self):
        """Persist index to disk."""
        if not self.persist_path:
            return

        data = {
            "entries": {
                k: {
                    "key": v.key,
                    "path": v.path,
                    "checksum": v.checksum,
                    "metadata": v.metadata,
                    "tags": list(v.tags),
                }
                for k, v in self._entries.items()
            }
        }

        with open(self.persist_path, 'w') as f:
            json.dump(data, f)

    def _load(self):
        """Load index from disk."""
        if not self.persist_path:
            return

        try:
            with open(self.persist_path) as f:
                data = json.load(f)

            for entry_data in data.get("entries", {}).values():
                self.index(
                    key=entry_data["key"],
                    path=entry_data["path"],
                    metadata=entry_data.get("metadata", {}),
                    tags=set(entry_data.get("tags", [])),
                )
        except:
            pass  # Start fresh on error
