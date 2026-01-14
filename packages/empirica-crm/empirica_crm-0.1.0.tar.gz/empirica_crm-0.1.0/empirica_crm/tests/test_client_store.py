"""
Tests for ClientStore - client CRUD operations.
"""

import pytest
from empirica_crm.client_store import ClientStore, Client


class TestClientStore:
    """Test suite for ClientStore."""

    def test_create_client(self, initialized_db, sample_client_data):
        """Test creating a new client."""
        store = ClientStore()
        try:
            client = store.create(**sample_client_data)

            assert client is not None
            assert client.client_id is not None
            assert client.name == sample_client_data["name"]
            assert client.client_type == sample_client_data["client_type"]
            assert client.status == "active"
            assert client.tags == sample_client_data["tags"]
        finally:
            store.close()

    def test_get_client(self, initialized_db, sample_client_data):
        """Test retrieving a client by ID."""
        store = ClientStore()
        try:
            created = store.create(**sample_client_data)
            retrieved = store.get(created.client_id)

            assert retrieved is not None
            assert retrieved.client_id == created.client_id
            assert retrieved.name == created.name
        finally:
            store.close()

    def test_get_nonexistent_client(self, initialized_db):
        """Test retrieving a nonexistent client."""
        store = ClientStore()
        try:
            result = store.get("nonexistent-uuid")
            assert result is None
        finally:
            store.close()

    def test_list_clients(self, initialized_db, sample_client_data):
        """Test listing clients."""
        store = ClientStore()
        try:
            # Create multiple clients
            store.create(**sample_client_data)
            store.create(name="Another Company", client_type="customer")

            clients = store.list()
            assert len(clients) >= 2
        finally:
            store.close()

    def test_list_clients_with_filter(self, initialized_db, sample_client_data):
        """Test listing clients with type filter."""
        store = ClientStore()
        try:
            store.create(**sample_client_data)
            store.create(name="Customer Co", client_type="customer")

            prospects = store.list(client_type="prospect")
            assert all(c.client_type == "prospect" for c in prospects)

            customers = store.list(client_type="customer")
            assert all(c.client_type == "customer" for c in customers)
        finally:
            store.close()

    def test_update_client(self, initialized_db, sample_client_data):
        """Test updating a client."""
        store = ClientStore()
        try:
            client = store.create(**sample_client_data)

            updated = store.update(
                client.client_id,
                name="Updated Company",
                next_action="New action",
            )

            assert updated is not None
            assert updated.name == "Updated Company"
            assert updated.next_action == "New action"
        finally:
            store.close()

    def test_archive_client(self, initialized_db, sample_client_data):
        """Test archiving (soft delete) a client."""
        store = ClientStore()
        try:
            client = store.create(**sample_client_data)

            success = store.archive(client.client_id)
            assert success is True

            archived = store.get(client.client_id)
            assert archived.status == "archived"

            # Should not appear in active list
            active = store.list(status="active")
            assert not any(c.client_id == client.client_id for c in active)
        finally:
            store.close()

    def test_add_contact(self, initialized_db, sample_client_data):
        """Test adding a contact to a client."""
        store = ClientStore()
        try:
            client = store.create(**sample_client_data)

            contact = {"name": "John Doe", "email": "john@test.com", "role": "CEO"}
            updated = store.update(client.client_id, add_contact=contact)

            assert updated is not None
            assert len(updated.contacts) == 1
            assert updated.contacts[0]["name"] == "John Doe"
        finally:
            store.close()

    def test_add_tag(self, initialized_db, sample_client_data):
        """Test adding a tag to a client."""
        store = ClientStore()
        try:
            client = store.create(**sample_client_data)
            original_tags = len(client.tags or [])

            updated = store.update(client.client_id, add_tag="new-tag")

            assert updated is not None
            assert "new-tag" in updated.tags
            assert len(updated.tags) == original_tags + 1
        finally:
            store.close()


class TestClient:
    """Test suite for Client dataclass."""

    def test_to_dict(self, initialized_db, sample_client_data):
        """Test Client.to_dict serialization."""
        store = ClientStore()
        try:
            client = store.create(**sample_client_data)
            data = client.to_dict()

            assert isinstance(data, dict)
            assert data["name"] == sample_client_data["name"]
            assert "client_id" in data
            assert "created_at" in data
        finally:
            store.close()
