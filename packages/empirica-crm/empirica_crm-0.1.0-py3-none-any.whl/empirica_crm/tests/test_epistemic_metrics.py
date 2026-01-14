"""
Tests for epistemic_metrics - computed metrics for client relationships.
"""

import pytest
from empirica_crm.client_store import ClientStore
from empirica_crm.engagement_store import EngagementStore
from empirica_crm.interaction_store import InteractionStore
from empirica_crm.epistemic_metrics import (
    compute_relationship_health,
    compute_knowledge_depth,
    compute_all_metrics,
    get_client_epistemic_state,
)


class TestRelationshipHealth:
    """Test suite for relationship health computation."""

    @pytest.fixture
    def client_with_activity(self, initialized_db):
        """Create a client with some interaction history."""
        client_store = ClientStore()
        interaction_store = InteractionStore()
        engagement_store = EngagementStore()

        try:
            # Create client
            client = client_store.create(name="Active Client", client_type="customer")

            # Add interactions
            interaction_store.log(
                client_id=client.client_id,
                summary="Initial call",
                interaction_type="call",
                sentiment="positive",
            )
            interaction_store.log(
                client_id=client.client_id,
                summary="Follow-up email",
                interaction_type="email",
                sentiment="neutral",
            )

            # Add engagement
            eng = engagement_store.create(
                client_id=client.client_id,
                title="Project X",
                engagement_type="project",
            )
            engagement_store.complete(eng.engagement_id, outcome="won")

            return client.client_id
        finally:
            client_store.close()
            interaction_store.close()
            engagement_store.close()

    def test_compute_health_returns_score(self, client_with_activity):
        """Test that health computation returns a valid score."""
        result = compute_relationship_health(client_with_activity)

        assert "relationship_health" in result
        assert 0 <= result["relationship_health"] <= 1

    def test_compute_health_returns_breakdown(self, client_with_activity):
        """Test that health computation includes breakdown."""
        result = compute_relationship_health(client_with_activity)

        assert "breakdown" in result
        breakdown = result["breakdown"]
        assert "frequency_score" in breakdown
        assert "sentiment_score" in breakdown
        assert "outcome_score" in breakdown

    def test_compute_health_returns_raw_data(self, client_with_activity):
        """Test that health computation includes raw data."""
        result = compute_relationship_health(client_with_activity)

        assert "raw_data" in result
        raw = result["raw_data"]
        assert "total_interactions" in raw
        assert raw["total_interactions"] >= 2

    def test_compute_health_for_inactive_client(self, initialized_db):
        """Test health computation for client with no activity."""
        client_store = ClientStore()
        try:
            client = client_store.create(name="Inactive Client")
            result = compute_relationship_health(client.client_id)

            # Should still return valid score (neutral defaults)
            assert "relationship_health" in result
            assert 0 <= result["relationship_health"] <= 1
        finally:
            client_store.close()


class TestKnowledgeDepth:
    """Test suite for knowledge depth computation."""

    @pytest.fixture
    def client_with_memory(self, initialized_db):
        """Create a client with some memory items."""
        from empirica_crm.client_memory import log_client_finding, log_client_unknown

        client_store = ClientStore()
        try:
            client = client_store.create(name="Knowledgeable Client")

            # Add findings
            log_client_finding(
                client_id=client.client_id,
                finding="Client prefers morning meetings",
                impact=0.7,
            )
            log_client_finding(
                client_id=client.client_id,
                finding="Budget is $50k-100k range",
                impact=0.9,
            )

            # Add unknown
            log_client_unknown(
                client_id=client.client_id,
                unknown="What is their timeline?",
            )

            return client.client_id
        finally:
            client_store.close()

    def test_compute_depth_returns_score(self, client_with_memory):
        """Test that depth computation returns a valid score."""
        result = compute_knowledge_depth(client_with_memory)

        assert "knowledge_depth" in result
        assert 0 <= result["knowledge_depth"] <= 1

    def test_compute_depth_returns_breakdown(self, client_with_memory):
        """Test that depth computation includes breakdown."""
        result = compute_knowledge_depth(client_with_memory)

        assert "breakdown" in result
        breakdown = result["breakdown"]
        assert "volume_score" in breakdown
        assert "confidence_score" in breakdown
        assert "resolution_score" in breakdown

    def test_compute_depth_returns_raw_data(self, client_with_memory):
        """Test that depth computation includes raw data."""
        result = compute_knowledge_depth(client_with_memory)

        assert "raw_data" in result
        raw = result["raw_data"]
        assert "finding_count" in raw
        assert "unknown_count" in raw


class TestComputeAllMetrics:
    """Test suite for combined metrics computation."""

    @pytest.fixture
    def complete_client(self, initialized_db):
        """Create a client with activity and memory."""
        from empirica_crm.client_memory import log_client_finding

        client_store = ClientStore()
        interaction_store = InteractionStore()

        try:
            client = client_store.create(name="Complete Client")

            interaction_store.log(
                client_id=client.client_id,
                summary="Test interaction",
                sentiment="positive",
            )

            log_client_finding(
                client_id=client.client_id,
                finding="Test finding",
                impact=0.7,
            )

            return client.client_id
        finally:
            client_store.close()
            interaction_store.close()

    def test_compute_all_returns_both_metrics(self, complete_client):
        """Test that compute_all_metrics returns both scores."""
        result = compute_all_metrics(complete_client)

        assert "relationship_health" in result
        assert "knowledge_depth" in result
        assert 0 <= result["relationship_health"] <= 1
        assert 0 <= result["knowledge_depth"] <= 1

    def test_compute_all_can_update_client(self, complete_client):
        """Test that metrics can update the client record."""
        result = compute_all_metrics(complete_client, update_client=True)

        assert result.get("client_updated") is True

        # Verify client was updated
        from empirica_crm.client_store import ClientStore
        store = ClientStore()
        try:
            client = store.get(complete_client)
            assert client.relationship_health > 0
        finally:
            store.close()


class TestGetClientEpistemicState:
    """Test suite for full epistemic state retrieval."""

    @pytest.fixture
    def client_id(self, initialized_db):
        """Create a test client."""
        store = ClientStore()
        try:
            client = store.create(name="State Test Client")
            return client.client_id
        finally:
            store.close()

    def test_get_state_returns_client_info(self, client_id):
        """Test that state includes client info."""
        result = get_client_epistemic_state(client_id)

        assert "client" in result
        assert result["client"]["client_id"] == client_id
        assert result["client"]["name"] == "State Test Client"

    def test_get_state_returns_metrics(self, client_id):
        """Test that state includes metrics."""
        result = get_client_epistemic_state(client_id)

        assert "metrics" in result
        metrics = result["metrics"]
        assert "relationship_health" in metrics
        assert "knowledge_depth" in metrics

    def test_get_state_returns_memory(self, client_id):
        """Test that state includes memory context."""
        result = get_client_epistemic_state(client_id)

        assert "memory" in result
        memory = result["memory"]
        assert "top_findings" in memory
        assert "open_unknowns" in memory
        assert "patterns" in memory

    def test_get_state_returns_actions(self, client_id):
        """Test that state includes action items."""
        result = get_client_epistemic_state(client_id)

        assert "actions" in result
        actions = result["actions"]
        assert "next_action" in actions
        assert "pending_follow_ups" in actions

    def test_get_state_for_nonexistent_client(self, initialized_db):
        """Test getting state for nonexistent client."""
        result = get_client_epistemic_state("nonexistent-id")

        assert "error" in result
