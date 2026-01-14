"""
Tests for EngagementStore - engagement lifecycle operations.
"""

import pytest
from empirica_crm.client_store import ClientStore
from empirica_crm.engagement_store import EngagementStore, Engagement


class TestEngagementStore:
    """Test suite for EngagementStore."""

    @pytest.fixture
    def client_id(self, initialized_db):
        """Create a test client and return its ID."""
        store = ClientStore()
        try:
            client = store.create(name="Test Client", client_type="prospect")
            return client.client_id
        finally:
            store.close()

    def test_create_engagement(self, initialized_db, client_id, sample_engagement_data):
        """Test creating a new engagement."""
        store = EngagementStore()
        try:
            engagement = store.create(client_id=client_id, **sample_engagement_data)

            assert engagement is not None
            assert engagement.engagement_id is not None
            assert engagement.client_id == client_id
            assert engagement.title == sample_engagement_data["title"]
            assert engagement.status == "active"
        finally:
            store.close()

    def test_get_engagement(self, initialized_db, client_id, sample_engagement_data):
        """Test retrieving an engagement by ID."""
        store = EngagementStore()
        try:
            created = store.create(client_id=client_id, **sample_engagement_data)
            retrieved = store.get(created.engagement_id)

            assert retrieved is not None
            assert retrieved.engagement_id == created.engagement_id
            assert retrieved.title == created.title
        finally:
            store.close()

    def test_list_engagements(self, initialized_db, client_id, sample_engagement_data):
        """Test listing engagements."""
        store = EngagementStore()
        try:
            store.create(client_id=client_id, **sample_engagement_data)
            store.create(client_id=client_id, title="Second Engagement")

            engagements = store.list(client_id=client_id)
            assert len(engagements) >= 2
        finally:
            store.close()

    def test_update_engagement(self, initialized_db, client_id, sample_engagement_data):
        """Test updating an engagement."""
        store = EngagementStore()
        try:
            engagement = store.create(client_id=client_id, **sample_engagement_data)

            updated = store.update(
                engagement.engagement_id,
                title="Updated Title",
                status="stalled",
            )

            assert updated is not None
            assert updated.title == "Updated Title"
            assert updated.status == "stalled"
        finally:
            store.close()

    def test_complete_engagement_won(self, initialized_db, client_id, sample_engagement_data):
        """Test completing an engagement with 'won' outcome."""
        store = EngagementStore()
        try:
            engagement = store.create(client_id=client_id, **sample_engagement_data)

            completed = store.complete(
                engagement.engagement_id,
                outcome="won",
                outcome_notes="Signed contract",
                actual_value=15000.0,
            )

            assert completed is not None
            assert completed.status == "completed"
            assert completed.outcome == "won"
            assert completed.outcome_notes == "Signed contract"
            assert completed.actual_value == 15000.0
        finally:
            store.close()

    def test_complete_engagement_lost(self, initialized_db, client_id, sample_engagement_data):
        """Test completing an engagement with 'lost' outcome."""
        store = EngagementStore()
        try:
            engagement = store.create(client_id=client_id, **sample_engagement_data)

            completed = store.complete(
                engagement.engagement_id,
                outcome="lost",
                outcome_notes="Went with competitor",
            )

            assert completed is not None
            assert completed.status == "completed"
            assert completed.outcome == "lost"
        finally:
            store.close()

    def test_get_client_engagements(self, initialized_db, client_id, sample_engagement_data):
        """Test getting engagements for a specific client."""
        store = EngagementStore()
        try:
            store.create(client_id=client_id, **sample_engagement_data)
            store.create(client_id=client_id, title="Second")

            engagements = store.get_client_engagements(client_id)
            assert len(engagements) >= 2
            assert all(e.client_id == client_id for e in engagements)
        finally:
            store.close()

    def test_get_client_engagements_active_only(self, initialized_db, client_id, sample_engagement_data):
        """Test filtering for active engagements only."""
        store = EngagementStore()
        try:
            e1 = store.create(client_id=client_id, **sample_engagement_data)
            store.create(client_id=client_id, title="Second")

            # Complete one
            store.complete(e1.engagement_id, outcome="won")

            active = store.get_client_engagements(client_id, active_only=True)
            assert all(e.status == "active" for e in active)
        finally:
            store.close()

    def test_days_active_property(self, initialized_db, client_id, sample_engagement_data):
        """Test days_active property calculation."""
        store = EngagementStore()
        try:
            engagement = store.create(client_id=client_id, **sample_engagement_data)

            # Newly created should be 0 days active
            assert engagement.days_active >= 0
        finally:
            store.close()


class TestEngagement:
    """Test suite for Engagement dataclass."""

    def test_to_dict(self, initialized_db, sample_engagement_data):
        """Test Engagement.to_dict serialization."""
        # Create client inline
        from empirica_crm.client_store import ClientStore
        client_store = ClientStore()
        try:
            client = client_store.create(name="Dict Test Client")
            client_id = client.client_id
        finally:
            client_store.close()

        store = EngagementStore()
        try:
            engagement = store.create(client_id=client_id, **sample_engagement_data)
            data = engagement.to_dict()

            assert isinstance(data, dict)
            assert data["title"] == sample_engagement_data["title"]
            assert "engagement_id" in data
            assert "status" in data
        finally:
            store.close()
