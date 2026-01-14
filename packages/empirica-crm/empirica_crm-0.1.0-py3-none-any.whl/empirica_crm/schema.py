"""
CRM Schema

Database table schemas for CRM module.
Extends Empirica's sessions.db with CRM-specific tables.

Usage:
    from empirica_crm.schema import ensure_schema
    ensure_schema()  # Creates tables if they don't exist
"""

import logging

logger = logging.getLogger(__name__)

CRM_SCHEMAS = [
    # Clients: Persistent relationship entities
    """
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,

        -- Knowledge base links
        notebooklm_url TEXT,
        knowledge_base_urls TEXT,  -- JSON array of additional URLs

        -- Contact information
        contacts TEXT,  -- JSON array: [{name, email, role, notes}]

        -- Classification
        client_type TEXT DEFAULT 'prospect',  -- prospect, active, partner, churned
        industry TEXT,
        tags TEXT,  -- JSON array

        -- Metadata
        created_at REAL NOT NULL,
        updated_at REAL,
        created_by_ai_id TEXT,

        -- Epistemic state (aggregate across engagements)
        relationship_health REAL DEFAULT 0.5,  -- 0.0-1.0
        engagement_frequency REAL DEFAULT 0.0,  -- interactions per week
        knowledge_depth REAL DEFAULT 0.0,  -- how well do I know them

        -- Status
        status TEXT DEFAULT 'active',  -- active, inactive, archived
        last_contact_at REAL,
        next_action TEXT,
        next_action_due REAL
    )
    """,

    # Engagements: Time-bounded client interactions
    """
    CREATE TABLE IF NOT EXISTS engagements (
        engagement_id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,

        -- What is this engagement about
        title TEXT NOT NULL,
        description TEXT,
        engagement_type TEXT DEFAULT 'outreach',  -- outreach, demo, negotiation, support, review

        -- Linked goal (optional)
        goal_id TEXT,

        -- Timeline
        started_at REAL NOT NULL,
        ended_at REAL,
        status TEXT DEFAULT 'active',  -- active, completed, stalled, lost

        -- Outcome tracking
        outcome TEXT,  -- won, lost, deferred, ongoing
        outcome_notes TEXT,

        -- Value tracking (optional)
        estimated_value REAL,
        actual_value REAL,
        currency TEXT DEFAULT 'USD',

        FOREIGN KEY (client_id) REFERENCES clients(client_id)
    )
    """,

    # Client-scoped findings (links existing findings to clients)
    """
    CREATE TABLE IF NOT EXISTS client_findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        finding_id TEXT NOT NULL,
        relevance REAL DEFAULT 1.0,  -- how relevant is this finding to client
        created_at REAL NOT NULL,

        FOREIGN KEY (client_id) REFERENCES clients(client_id),
        UNIQUE(client_id, finding_id)
    )
    """,

    # Client-scoped unknowns
    """
    CREATE TABLE IF NOT EXISTS client_unknowns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        unknown_id TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',  -- critical, high, medium, low
        created_at REAL NOT NULL,

        FOREIGN KEY (client_id) REFERENCES clients(client_id),
        UNIQUE(client_id, unknown_id)
    )
    """,

    # Client interactions log (lightweight activity tracking)
    """
    CREATE TABLE IF NOT EXISTS client_interactions (
        interaction_id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        engagement_id TEXT,
        session_id TEXT,

        -- What happened
        interaction_type TEXT NOT NULL,  -- email, call, meeting, demo, document
        summary TEXT NOT NULL,

        -- Who was involved
        contacts_involved TEXT,  -- JSON array of contact names
        ai_id TEXT,

        -- When
        occurred_at REAL NOT NULL,

        -- Sentiment/outcome
        sentiment TEXT,  -- positive, neutral, negative
        follow_up_required INTEGER DEFAULT 0,
        follow_up_notes TEXT,

        FOREIGN KEY (client_id) REFERENCES clients(client_id),
        FOREIGN KEY (engagement_id) REFERENCES engagements(engagement_id)
    )
    """,

    # Client memory: Embedded semantic memory items (Qdrant-backed with SQLite fallback)
    """
    CREATE TABLE IF NOT EXISTS client_memory (
        item_id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        content TEXT NOT NULL,
        content_hash TEXT,  -- MD5 for deduplication
        memory_type TEXT NOT NULL,  -- finding, unknown, pattern, preference, constraint
        engagement_id TEXT,
        session_id TEXT,
        confidence REAL DEFAULT 0.5,
        impact REAL DEFAULT 0.5,
        is_resolved INTEGER DEFAULT 0,
        resolved_by TEXT,
        resolved_at REAL,
        tags TEXT,  -- JSON array
        created_at REAL NOT NULL,
        updated_at REAL,

        FOREIGN KEY (client_id) REFERENCES clients(client_id),
        FOREIGN KEY (engagement_id) REFERENCES engagements(engagement_id)
    )
    """,

    # Indexes for performance
    "CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status)",
    "CREATE INDEX IF NOT EXISTS idx_clients_type ON clients(client_type)",
    "CREATE INDEX IF NOT EXISTS idx_engagements_client ON engagements(client_id)",
    "CREATE INDEX IF NOT EXISTS idx_engagements_status ON engagements(status)",
    "CREATE INDEX IF NOT EXISTS idx_client_findings_client ON client_findings(client_id)",
    "CREATE INDEX IF NOT EXISTS idx_client_unknowns_client ON client_unknowns(client_id)",
    "CREATE INDEX IF NOT EXISTS idx_interactions_client ON client_interactions(client_id)",
    "CREATE INDEX IF NOT EXISTS idx_interactions_date ON client_interactions(occurred_at)",
    "CREATE INDEX IF NOT EXISTS idx_client_memory_client ON client_memory(client_id)",
    "CREATE INDEX IF NOT EXISTS idx_client_memory_type ON client_memory(memory_type)",
    "CREATE INDEX IF NOT EXISTS idx_client_memory_hash ON client_memory(content_hash)",
]


def ensure_schema(db_connection=None):
    """
    Ensure CRM tables exist in the database.

    Args:
        db_connection: SQLite connection. If None, uses empirica's default database.

    Returns:
        bool: True if schema was created/verified successfully
    """
    if db_connection is None:
        # Import from empirica to get the standard database path
        from empirica.config.path_resolver import get_session_db_path
        import sqlite3

        db_path = get_session_db_path()
        conn = sqlite3.connect(str(db_path))
        owns_connection = True
    else:
        conn = db_connection
        owns_connection = False

    try:
        cursor = conn.cursor()
        for schema in CRM_SCHEMAS:
            try:
                cursor.execute(schema)
            except Exception as e:
                logger.debug(f"Schema execution note: {e}")
        conn.commit()
        logger.info("✓ CRM schema verified/created")
        return True
    except Exception as e:
        logger.error(f"Failed to ensure CRM schema: {e}")
        return False
    finally:
        if owns_connection:
            conn.close()
