"""
Client Memory - Qdrant-backed semantic memory for CRM

Enables relational epistemics by embedding client-scoped knowledge:
- Client findings (what we learned about them)
- Client unknowns (what we need to learn)
- Client patterns (behavioral patterns, preferences)

Uses Empirica's Qdrant infrastructure for embeddings and search.
Gracefully degrades when Qdrant is not available.

Architecture:
- MemoryBackend protocol defines storage interface
- QdrantMemoryBackend provides semantic search with SQLite persistence
- SQLiteMemoryBackend provides keyword-based fallback
- Factory function get_backend() returns appropriate backend
"""

import uuid
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional

from .memory_backend import MemoryItem, get_backend

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
ClientMemoryItem = MemoryItem


# =============================================================================
# Core API (Backend-Agnostic)
# =============================================================================

def embed_client_memory(
    client_id: str,
    content: str,
    memory_type: str = "finding",
    engagement_id: str = None,
    session_id: str = None,
    confidence: float = 0.5,
    impact: float = 0.5,
    tags: List[str] = None,
) -> Optional[str]:
    """
    Embed a client memory item.

    Uses Qdrant for semantic search when available, falls back to SQLite.

    Args:
        client_id: Client UUID
        content: The memory content to embed
        memory_type: finding, unknown, pattern, preference, constraint
        engagement_id: Optional linked engagement
        session_id: Optional session ID
        confidence: Confidence in this memory (0-1)
        impact: Impact/importance (0-1)
        tags: Optional tags for filtering

    Returns:
        Item ID if successful, None on failure
    """
    item = MemoryItem(
        item_id=str(uuid.uuid4()),
        client_id=client_id,
        content=content,
        memory_type=memory_type,
        engagement_id=engagement_id,
        session_id=session_id,
        confidence=confidence,
        impact=impact,
        tags=tags,
        created_at=time.time(),
    )

    backend = get_backend(client_id)
    return backend.store(item)


def search_client_memory(
    client_id: str,
    query: str,
    memory_type: str = None,
    min_confidence: float = 0.0,
    min_impact: float = 0.0,
    limit: int = 10,
) -> List[Dict]:
    """
    Semantic search over client memory.

    Uses Qdrant for vector similarity when available, keyword search otherwise.

    Args:
        client_id: Client UUID
        query: Search query
        memory_type: Filter by type (finding, unknown, pattern, etc.)
        min_confidence: Minimum confidence threshold
        min_impact: Minimum impact threshold
        limit: Maximum results

    Returns:
        List of matching memory items with scores
    """
    backend = get_backend(client_id)
    results = backend.search(client_id, query, memory_type, limit)

    # Apply post-filters
    if min_confidence > 0 or min_impact > 0:
        results = [
            r for r in results
            if r.get("confidence", 0) >= min_confidence
            and r.get("impact", 0) >= min_impact
        ]

    return results


def get_client_context(client_id: str, limit: int = 10) -> Dict[str, List[Dict]]:
    """
    Get comprehensive client context for AI grounding.

    Returns findings, unknowns, and patterns sorted by relevance.

    Args:
        client_id: Client UUID
        limit: Max items per category

    Returns:
        Dict with 'findings', 'unknowns', 'patterns' lists
    """
    backend = get_backend(client_id)

    context = {
        "findings": backend.get_by_type(client_id, "finding", limit),
        "unknowns": backend.get_by_type(client_id, "unknown", limit),
        "patterns": backend.get_by_type(client_id, "pattern", limit),
    }

    return context


def resolve_unknown(
    client_id: str,
    item_id: str,
    resolved_by: str,
) -> bool:
    """
    Mark an unknown as resolved.

    Args:
        client_id: Client UUID
        item_id: The unknown item ID
        resolved_by: Resolution text

    Returns:
        True if successful
    """
    backend = get_backend(client_id)
    return backend.resolve(client_id, item_id, resolved_by)


def confirm_finding(
    client_id: str,
    content: str,
    session_id: str = None,
    confidence_boost: float = 0.1,
) -> bool:
    """
    Confirm an existing finding, boosting confidence.

    If the finding doesn't exist, creates it. Otherwise, updates confidence.

    Args:
        client_id: Client UUID
        content: The finding content
        session_id: Optional session ID
        confidence_boost: Amount to boost confidence

    Returns:
        True if successful
    """
    backend = get_backend(client_id)
    content_hash = hashlib.md5(content.encode()).hexdigest()

    existing_id = backend.find_by_hash(client_id, content_hash)

    if existing_id:
        return backend.boost_confidence(existing_id, session_id, confidence_boost)
    else:
        item_id = embed_client_memory(
            client_id=client_id,
            content=content,
            memory_type="finding",
            session_id=session_id,
            confidence=0.5 + confidence_boost,
            impact=0.5,
        )
        return item_id is not None


# =============================================================================
# Convenience Functions
# =============================================================================

def log_client_finding(
    client_id: str,
    finding: str,
    impact: float = 0.5,
    engagement_id: str = None,
    session_id: str = None,
    tags: List[str] = None,
) -> Optional[str]:
    """Convenience function to log a client finding."""
    return embed_client_memory(
        client_id=client_id,
        content=finding,
        memory_type="finding",
        engagement_id=engagement_id,
        session_id=session_id,
        impact=impact,
        tags=tags,
    )


def log_client_unknown(
    client_id: str,
    unknown: str,
    engagement_id: str = None,
    session_id: str = None,
    tags: List[str] = None,
) -> Optional[str]:
    """Convenience function to log a client unknown."""
    return embed_client_memory(
        client_id=client_id,
        content=unknown,
        memory_type="unknown",
        engagement_id=engagement_id,
        session_id=session_id,
        impact=0.7,  # Unknowns are high impact by default
        tags=tags,
    )


def log_client_pattern(
    client_id: str,
    pattern: str,
    confidence: float = 0.5,
    engagement_id: str = None,
    session_id: str = None,
    tags: List[str] = None,
) -> Optional[str]:
    """Convenience function to log a client behavioral pattern."""
    return embed_client_memory(
        client_id=client_id,
        content=pattern,
        memory_type="pattern",
        confidence=confidence,
        engagement_id=engagement_id,
        session_id=session_id,
        impact=0.6,
        tags=tags,
    )


