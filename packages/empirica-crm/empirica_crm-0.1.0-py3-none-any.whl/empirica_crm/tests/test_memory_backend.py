"""
Tests for memory_backend - MemoryBackend protocol and implementations.
"""

import pytest
from empirica_crm.memory_backend import (
    MemoryItem,
    MemoryBackend,
    SQLiteMemoryBackend,
    QdrantMemoryBackend,
    SQLiteConnection,
    get_backend,
)


class TestMemoryItem:
    """Test suite for MemoryItem dataclass."""

    def test_create_memory_item(self):
        """Test creating a MemoryItem."""
        item = MemoryItem(
            item_id="test-id",
            client_id="client-123",
            content="Test content",
            memory_type="finding",
        )

        assert item.item_id == "test-id"
        assert item.client_id == "client-123"
        assert item.content == "Test content"
        assert item.memory_type == "finding"
        assert item.confidence == 0.5  # default
        assert item.impact == 0.5  # default

    def test_content_hash(self):
        """Test content_hash property."""
        item = MemoryItem(
            item_id="test-id",
            client_id="client-123",
            content="Test content",
            memory_type="finding",
        )

        assert item.content_hash is not None
        assert len(item.content_hash) == 32  # MD5 hex

        # Same content = same hash
        item2 = MemoryItem(
            item_id="other-id",
            client_id="other-client",
            content="Test content",
            memory_type="unknown",
        )
        assert item.content_hash == item2.content_hash

    def test_score_property(self):
        """Test score property calculation."""
        item = MemoryItem(
            item_id="test-id",
            client_id="client-123",
            content="Test",
            memory_type="finding",
            confidence=0.8,
            impact=0.6,
        )

        assert item.score == 0.8 * 0.6  # 0.48

    def test_to_dict(self):
        """Test to_dict serialization."""
        item = MemoryItem(
            item_id="test-id",
            client_id="client-123",
            content="Test content",
            memory_type="finding",
            tags=["test"],
        )

        data = item.to_dict()
        assert isinstance(data, dict)
        assert data["item_id"] == "test-id"
        assert data["tags"] == ["test"]


class TestSQLiteMemoryBackend:
    """Test suite for SQLiteMemoryBackend."""

    def test_store_memory(self, initialized_db):
        """Test storing a memory item."""
        backend = SQLiteMemoryBackend()
        item = MemoryItem(
            item_id="test-id-1",
            client_id="client-123",
            content="Test finding content",
            memory_type="finding",
            confidence=0.7,
            impact=0.8,
        )

        result = backend.store(item)
        assert result == "test-id-1"

    def test_search_memory(self, initialized_db):
        """Test searching for memory items."""
        backend = SQLiteMemoryBackend()

        # Store some items
        backend.store(MemoryItem(
            item_id="id-1",
            client_id="client-abc",
            content="First finding about technology",
            memory_type="finding",
        ))
        backend.store(MemoryItem(
            item_id="id-2",
            client_id="client-abc",
            content="Unknown about budget",
            memory_type="unknown",
        ))

        # Search for technology
        results = backend.search("client-abc", "technology")
        assert len(results) >= 1
        assert any("technology" in r["content"] for r in results)

    def test_search_by_type(self, initialized_db):
        """Test filtering search by memory type."""
        backend = SQLiteMemoryBackend()

        backend.store(MemoryItem(
            item_id="f1",
            client_id="client-xyz",
            content="Finding one",
            memory_type="finding",
        ))
        backend.store(MemoryItem(
            item_id="u1",
            client_id="client-xyz",
            content="Unknown one",
            memory_type="unknown",
        ))

        findings = backend.search("client-xyz", "", memory_type="finding")
        assert all(r["memory_type"] == "finding" for r in findings)

    def test_resolve_memory(self, initialized_db):
        """Test resolving a memory item."""
        backend = SQLiteMemoryBackend()

        item = MemoryItem(
            item_id="resolve-test",
            client_id="client-123",
            content="Unknown to resolve",
            memory_type="unknown",
        )
        backend.store(item)

        result = backend.resolve("client-123", "resolve-test", "Found the answer")
        assert result is True

    def test_find_by_hash(self, initialized_db):
        """Test finding item by content hash."""
        backend = SQLiteMemoryBackend()

        item = MemoryItem(
            item_id="hash-test",
            client_id="client-123",
            content="Unique content for hash test",
            memory_type="finding",
        )
        backend.store(item)

        found_id = backend.find_by_hash("client-123", item.content_hash)
        assert found_id == "hash-test"

    def test_boost_confidence(self, initialized_db):
        """Test boosting confidence of an item."""
        backend = SQLiteMemoryBackend()

        item = MemoryItem(
            item_id="boost-test",
            client_id="client-123",
            content="Finding to boost",
            memory_type="finding",
            confidence=0.5,
        )
        backend.store(item)

        result = backend.boost_confidence("boost-test", None, 0.1)
        assert result is True


class TestQdrantMemoryBackend:
    """Test suite for QdrantMemoryBackend with mocked Qdrant."""

    def test_falls_back_to_sqlite_when_unavailable(self, initialized_db, mock_qdrant_unavailable):
        """Test that QdrantMemoryBackend falls back to SQLite."""
        backend = QdrantMemoryBackend("client-123")

        item = MemoryItem(
            item_id="fallback-test",
            client_id="client-123",
            content="Test content",
            memory_type="finding",
        )

        # Should still work via SQLite fallback
        result = backend.store(item)
        assert result == "fallback-test"

    def test_search_falls_back_to_sqlite(self, initialized_db, mock_qdrant_unavailable):
        """Test search falls back to SQLite when Qdrant unavailable."""
        backend = QdrantMemoryBackend("client-456")

        # Store via SQLite
        item = MemoryItem(
            item_id="search-fallback",
            client_id="client-456",
            content="Searchable content",
            memory_type="finding",
        )
        backend.store(item)

        # Search should use SQLite
        results = backend.search("client-456", "Searchable")
        assert len(results) >= 1


class TestGetBackend:
    """Test suite for get_backend factory function."""

    def test_returns_qdrant_backend(self):
        """Test that get_backend returns QdrantMemoryBackend."""
        backend = get_backend("test-client")
        assert isinstance(backend, QdrantMemoryBackend)

    def test_different_clients_get_different_backends(self):
        """Test that different clients get separate backend instances."""
        backend1 = get_backend("client-1")
        backend2 = get_backend("client-2")

        assert backend1.client_id == "client-1"
        assert backend2.client_id == "client-2"


class TestSQLiteConnection:
    """Test suite for SQLiteConnection singleton."""

    def test_singleton_pattern(self, initialized_db):
        """Test that SQLiteConnection is a singleton."""
        conn1 = SQLiteConnection.get_instance()
        conn2 = SQLiteConnection.get_instance()

        assert conn1 is conn2

    def test_context_manager(self, initialized_db):
        """Test connection context manager."""
        conn = SQLiteConnection.get_instance()

        with conn.connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
