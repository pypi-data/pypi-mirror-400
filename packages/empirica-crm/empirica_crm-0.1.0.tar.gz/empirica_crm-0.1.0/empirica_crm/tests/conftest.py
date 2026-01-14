"""
Pytest fixtures for CRM tests.

Provides isolated test databases and common test data.
"""

import os
import tempfile
import sqlite3
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    db_path = tmp_path / "test_sessions.db"
    return db_path


@pytest.fixture
def mock_session_db(temp_db_path):
    """
    Patch get_session_db_path to use a temp database.

    Yields the database path after patching.
    """
    with patch("empirica.config.path_resolver.get_session_db_path") as mock:
        mock.return_value = temp_db_path
        yield temp_db_path


@pytest.fixture
def initialized_db(mock_session_db):
    """
    Initialize the temp database with CRM schema.

    Returns the database path.
    """
    from empirica_crm.schema import ensure_schema

    # Initialize schema
    conn = sqlite3.connect(str(mock_session_db))
    ensure_schema(conn)
    conn.close()

    return mock_session_db


@pytest.fixture
def sample_client_data():
    """Sample client data for tests."""
    return {
        "name": "Test Company",
        "description": "A test company for unit tests",
        "client_type": "prospect",
        "industry": "Technology",
        "tags": ["test", "unit-test"],
        "next_action": "Follow up on demo",
    }


@pytest.fixture
def sample_engagement_data():
    """Sample engagement data for tests."""
    return {
        "title": "Demo Meeting",
        "description": "Product demonstration",
        "engagement_type": "meeting",
        "estimated_value": 10000.0,
        "currency": "USD",
    }


@pytest.fixture
def sample_interaction_data():
    """Sample interaction data for tests."""
    return {
        "summary": "Initial call to discuss needs",
        "interaction_type": "call",
        "sentiment": "positive",
        "follow_up_required": True,
        "follow_up_notes": "Send proposal",
    }


@pytest.fixture
def mock_qdrant_unavailable():
    """Mock Qdrant as unavailable."""
    with patch("empirica_crm.memory_backend.QdrantMemoryBackend._check_available") as mock:
        mock.return_value = False
        yield mock


@pytest.fixture
def mock_qdrant_available():
    """Mock Qdrant as available with mock client."""
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    mock_client.query_points.return_value = MagicMock(points=[])
    mock_client.scroll.return_value = ([], None)

    with patch("empirica_crm.memory_backend.QdrantMemoryBackend._check_available") as check_mock:
        check_mock.return_value = True
        with patch("empirica_crm.memory_backend.QdrantMemoryBackend._get_client") as client_mock:
            client_mock.return_value = mock_client
            with patch("empirica_crm.memory_backend.QdrantMemoryBackend._get_embedding") as embed_mock:
                embed_mock.return_value = [0.1] * 1536
                yield {
                    "client": mock_client,
                    "check": check_mock,
                    "embed": embed_mock,
                }
