"""
Memory Backend Abstractions

Provides protocol-based abstraction over storage backends (Qdrant, SQLite).
Enables clean separation of concerns and easier testing.
"""

import json
import hashlib
import time
import logging
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """A memory item stored in any backend."""
    item_id: str
    client_id: str
    content: str
    memory_type: str  # finding, unknown, pattern, preference, constraint
    engagement_id: Optional[str] = None
    session_id: Optional[str] = None
    confidence: float = 0.5
    impact: float = 0.5
    is_resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[float] = None
    tags: Optional[List[str]] = None
    created_at: Optional[float] = None
    updated_at: Optional[float] = None

    @property
    def content_hash(self) -> str:
        """MD5 hash for deduplication."""
        return hashlib.md5(self.content.encode()).hexdigest()

    @property
    def score(self) -> float:
        """Combined relevance score."""
        return self.confidence * self.impact

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@runtime_checkable
class MemoryBackend(Protocol):
    """Protocol for memory storage backends."""

    def store(self, item: MemoryItem) -> Optional[str]:
        """Store a memory item. Returns item_id or None on failure."""
        ...

    def search(
        self,
        client_id: str,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for memory items."""
        ...

    def get_by_type(
        self,
        client_id: str,
        memory_type: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get items by memory type."""
        ...

    def resolve(
        self,
        client_id: str,
        item_id: str,
        resolved_by: str,
    ) -> bool:
        """Mark an item as resolved."""
        ...

    def find_by_hash(
        self,
        client_id: str,
        content_hash: str,
    ) -> Optional[str]:
        """Find item by content hash."""
        ...

    def boost_confidence(
        self,
        item_id: str,
        session_id: Optional[str],
        boost: float,
    ) -> bool:
        """Boost confidence of an item."""
        ...


class SQLiteConnection:
    """Context-managed SQLite connection for CRM memory."""

    _instance: Optional["SQLiteConnection"] = None

    def __init__(self):
        self._conn: Optional[sqlite3.Connection] = None
        self._db_path: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "SQLiteConnection":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_db_path(self) -> str:
        """Get database path from empirica config."""
        if self._db_path is None:
            from empirica.config.path_resolver import get_session_db_path
            self._db_path = str(get_session_db_path())
        return self._db_path

    @contextmanager
    def connection(self):
        """Context manager for database connection."""
        conn = sqlite3.connect(self._get_db_path())
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ensure_schema(self):
        """Ensure client_memory table exists."""
        from .schema import CRM_SCHEMAS

        with self.connection() as conn:
            cursor = conn.cursor()
            for schema in CRM_SCHEMAS:
                if "client_memory" in schema:
                    try:
                        cursor.execute(schema)
                    except Exception:
                        pass


class SQLiteMemoryBackend:
    """SQLite implementation of MemoryBackend."""

    def __init__(self):
        self._db = SQLiteConnection.get_instance()
        self._db.ensure_schema()

    def store(self, item: MemoryItem) -> Optional[str]:
        """Store a memory item in SQLite."""
        try:
            tags_json = json.dumps(item.tags) if item.tags else None
            created_at = item.created_at or time.time()

            with self._db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO client_memory
                    (item_id, client_id, content, content_hash, memory_type,
                     engagement_id, session_id, confidence, impact, tags, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.item_id, item.client_id, item.content, item.content_hash,
                    item.memory_type, item.engagement_id, item.session_id,
                    item.confidence, item.impact, tags_json, created_at
                ))

            logger.debug(f"SQLite stored: {item.item_id[:8]}...")
            return item.item_id
        except Exception as e:
            logger.warning(f"SQLite store failed: {e}")
            return None

    def search(
        self,
        client_id: str,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Keyword-based search in SQLite."""
        try:
            with self._db.connection() as conn:
                cursor = conn.cursor()

                sql = """
                    SELECT item_id, client_id, content, memory_type, confidence, impact,
                           engagement_id, session_id, tags, is_resolved, created_at
                    FROM client_memory
                    WHERE client_id = ? AND (is_resolved = 0 OR is_resolved IS NULL)
                """
                params: List[Any] = [client_id]

                if memory_type:
                    sql += " AND memory_type = ?"
                    params.append(memory_type)

                if query:
                    sql += " AND content LIKE ?"
                    params.append(f"%{query}%")

                sql += " ORDER BY (confidence * impact) DESC LIMIT ?"
                params.append(limit)

                cursor.execute(sql, params)
                return self._rows_to_dicts(cursor.fetchall())
        except Exception as e:
            logger.warning(f"SQLite search failed: {e}")
            return []

    def get_by_type(
        self,
        client_id: str,
        memory_type: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get items by type."""
        return self.search(client_id, "", memory_type, limit)

    def resolve(
        self,
        client_id: str,
        item_id: str,
        resolved_by: str,
    ) -> bool:
        """Mark item as resolved."""
        try:
            now = time.time()
            with self._db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE client_memory
                    SET is_resolved = 1, resolved_by = ?, resolved_at = ?, updated_at = ?
                    WHERE item_id = ? AND client_id = ?
                """, (resolved_by, now, now, item_id, client_id))
            return True
        except Exception as e:
            logger.warning(f"SQLite resolve failed: {e}")
            return False

    def find_by_hash(
        self,
        client_id: str,
        content_hash: str,
    ) -> Optional[str]:
        """Find item by content hash."""
        try:
            with self._db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_id FROM client_memory
                    WHERE client_id = ? AND content_hash = ?
                    LIMIT 1
                """, (client_id, content_hash))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.debug(f"SQLite hash lookup failed: {e}")
            return None

    def boost_confidence(
        self,
        item_id: str,
        session_id: Optional[str],
        boost: float,
    ) -> bool:
        """Boost confidence of an item."""
        try:
            with self._db.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE client_memory
                    SET confidence = MIN(0.95, confidence + ?),
                        session_id = COALESCE(?, session_id),
                        updated_at = ?
                    WHERE item_id = ?
                """, (boost, session_id, time.time(), item_id))
            return True
        except Exception as e:
            logger.warning(f"SQLite boost failed: {e}")
            return False

    @staticmethod
    def _rows_to_dicts(rows) -> List[Dict[str, Any]]:
        """Convert SQLite rows to dicts."""
        results = []
        for row in rows:
            tags = row["tags"]
            if tags:
                try:
                    tags = json.loads(tags)
                except json.JSONDecodeError:
                    tags = []

            results.append({
                "item_id": row["item_id"],
                "content": row["content"],
                "memory_type": row["memory_type"],
                "confidence": row["confidence"] or 0.5,
                "impact": row["impact"] or 0.5,
                "engagement_id": row["engagement_id"],
                "tags": tags or [],
                "created_at": row["created_at"],
                "score": (row["confidence"] or 0.5) * (row["impact"] or 0.5),
            })
        return results


class QdrantMemoryBackend:
    """Qdrant implementation of MemoryBackend with SQLite fallback."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self._sqlite = SQLiteMemoryBackend()
        self._collection = f"crm_client_{client_id[:8]}_memory"
        self._qdrant_available: Optional[bool] = None

    def _check_available(self) -> bool:
        """Check if Qdrant is available."""
        if self._qdrant_available is not None:
            return self._qdrant_available

        try:
            from empirica.core.qdrant.vector_store import _check_qdrant_available
            self._qdrant_available = _check_qdrant_available()
            return self._qdrant_available
        except ImportError:
            self._qdrant_available = False
            return False

    def _get_client(self):
        """Get Qdrant client."""
        from empirica.core.qdrant.vector_store import _get_qdrant_client
        return _get_qdrant_client()

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text."""
        try:
            from empirica.core.qdrant.embeddings import get_embedding
            return get_embedding(text)
        except Exception as e:
            logger.debug(f"Embedding failed: {e}")
            return None

    def _ensure_collection(self):
        """Ensure Qdrant collection exists."""
        try:
            from qdrant_client.models import Distance, VectorParams
            from empirica.core.qdrant.embeddings import get_vector_size

            client = self._get_client()
            if not client.collection_exists(self._collection):
                vector_size = get_vector_size()
                client.create_collection(
                    self._collection,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {self._collection}")
        except Exception as e:
            logger.debug(f"Failed to ensure collection: {e}")

    def store(self, item: MemoryItem) -> Optional[str]:
        """Store in Qdrant with SQLite persistence."""
        # Always persist to SQLite
        self._sqlite.store(item)

        if not self._check_available():
            return item.item_id

        try:
            from qdrant_client.models import PointStruct

            self._ensure_collection()

            vector = self._get_embedding(item.content)
            if vector is None:
                return item.item_id

            payload = {
                "item_id": item.item_id,
                "client_id": item.client_id,
                "content": item.content[:500],
                "content_full": item.content if len(item.content) <= 500 else None,
                "content_hash": item.content_hash,
                "memory_type": item.memory_type,
                "engagement_id": item.engagement_id,
                "session_id": item.session_id,
                "confidence": item.confidence,
                "impact": item.impact,
                "is_resolved": item.is_resolved,
                "tags": item.tags or [],
                "created_at": item.created_at or time.time(),
            }

            point_id = int(hashlib.md5(item.item_id.encode()).hexdigest()[:15], 16)
            point = PointStruct(id=point_id, vector=vector, payload=payload)

            client = self._get_client()
            client.upsert(collection_name=self._collection, points=[point])

            logger.info(f"Qdrant stored: {item.memory_type} for {item.client_id[:8]}")
            return item.item_id
        except Exception as e:
            logger.warning(f"Qdrant store failed: {e}")
            return item.item_id

    def search(
        self,
        client_id: str,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Semantic search in Qdrant."""
        if not self._check_available():
            return self._sqlite.search(client_id, query, memory_type, limit)

        try:
            client = self._get_client()
            if not client.collection_exists(self._collection):
                return self._sqlite.search(client_id, query, memory_type, limit)

            vector = self._get_embedding(query)
            if vector is None:
                return self._sqlite.search(client_id, query, memory_type, limit)

            from qdrant_client.models import Filter, FieldCondition, MatchValue

            conditions = []
            if memory_type:
                conditions.append(FieldCondition(key="memory_type", match=MatchValue(value=memory_type)))

            query_filter = Filter(must=conditions) if conditions else None

            results = client.query_points(
                collection_name=self._collection,
                query=vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )

            return [
                {
                    "score": r.score,
                    "item_id": r.payload.get("item_id"),
                    "content": r.payload.get("content_full") or r.payload.get("content"),
                    "memory_type": r.payload.get("memory_type"),
                    "confidence": r.payload.get("confidence"),
                    "impact": r.payload.get("impact"),
                    "engagement_id": r.payload.get("engagement_id"),
                    "tags": r.payload.get("tags", []),
                    "created_at": r.payload.get("created_at"),
                }
                for r in results.points
            ]
        except Exception as e:
            logger.warning(f"Qdrant search failed: {e}")
            return self._sqlite.search(client_id, query, memory_type, limit)

    def get_by_type(
        self,
        client_id: str,
        memory_type: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get items by type from Qdrant."""
        if not self._check_available():
            return self._sqlite.get_by_type(client_id, memory_type, limit)

        try:
            client = self._get_client()
            if not client.collection_exists(self._collection):
                return self._sqlite.get_by_type(client_id, memory_type, limit)

            from qdrant_client.models import Filter, FieldCondition, MatchValue

            results = client.scroll(
                collection_name=self._collection,
                scroll_filter=Filter(
                    must=[FieldCondition(key="memory_type", match=MatchValue(value=memory_type))]
                ),
                limit=limit,
                with_payload=True,
            )

            points, _ = results
            items = [
                {
                    "item_id": p.payload.get("item_id"),
                    "content": p.payload.get("content_full") or p.payload.get("content"),
                    "confidence": p.payload.get("confidence"),
                    "impact": p.payload.get("impact"),
                    "tags": p.payload.get("tags", []),
                    "created_at": p.payload.get("created_at"),
                }
                for p in points
            ]

            # Sort by score
            items.sort(key=lambda x: (x.get("impact", 0) * x.get("confidence", 0)), reverse=True)
            return items
        except Exception as e:
            logger.warning(f"Qdrant get_by_type failed: {e}")
            return self._sqlite.get_by_type(client_id, memory_type, limit)

    def resolve(
        self,
        client_id: str,
        item_id: str,
        resolved_by: str,
    ) -> bool:
        """Mark item as resolved in both backends."""
        # Always update SQLite
        self._sqlite.resolve(client_id, item_id, resolved_by)

        if not self._check_available():
            return True

        try:
            client = self._get_client()
            if not client.collection_exists(self._collection):
                return True

            point_id = int(hashlib.md5(item_id.encode()).hexdigest()[:15], 16)
            results = client.retrieve(collection_name=self._collection, ids=[point_id], with_payload=True)

            if not results:
                return True

            point = results[0]
            payload = dict(point.payload)
            payload["is_resolved"] = True
            payload["resolved_by"] = resolved_by
            payload["resolved_at"] = time.time()

            from qdrant_client.models import PointStruct
            client.upsert(
                collection_name=self._collection,
                points=[PointStruct(id=point_id, vector=point.vector, payload=payload)]
            )
            return True
        except Exception as e:
            logger.warning(f"Qdrant resolve failed: {e}")
            return True

    def find_by_hash(
        self,
        client_id: str,
        content_hash: str,
    ) -> Optional[str]:
        """Find by hash (delegates to SQLite)."""
        return self._sqlite.find_by_hash(client_id, content_hash)

    def boost_confidence(
        self,
        item_id: str,
        session_id: Optional[str],
        boost: float,
    ) -> bool:
        """Boost confidence (delegates to SQLite)."""
        return self._sqlite.boost_confidence(item_id, session_id, boost)


def get_backend(client_id: str) -> MemoryBackend:
    """Factory to get appropriate memory backend for a client."""
    return QdrantMemoryBackend(client_id)
