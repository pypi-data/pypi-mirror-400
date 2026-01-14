"""
Interaction Store - CRUD operations for client interactions

Interactions are lightweight activity logs for client relationships.
Examples: emails sent, calls made, meetings held, demos given.
"""

import json
import uuid
import time
import logging
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class Interaction:
    """Interaction entity - lightweight activity log entry."""
    interaction_id: str
    client_id: str
    summary: str
    interaction_type: str = "email"  # email, call, meeting, demo, document, note
    engagement_id: Optional[str] = None
    session_id: Optional[str] = None
    contacts_involved: Optional[List[str]] = None
    ai_id: Optional[str] = None
    occurred_at: float = field(default_factory=time.time)
    sentiment: Optional[str] = None  # positive, neutral, negative
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Interaction":
        """Create Interaction from database row."""
        contacts = row.get('contacts_involved')
        if contacts and isinstance(contacts, str):
            try:
                contacts = json.loads(contacts)
            except json.JSONDecodeError:
                contacts = None

        return cls(
            interaction_id=row['interaction_id'],
            client_id=row['client_id'],
            summary=row['summary'],
            interaction_type=row.get('interaction_type', 'email'),
            engagement_id=row.get('engagement_id'),
            session_id=row.get('session_id'),
            contacts_involved=contacts,
            ai_id=row.get('ai_id'),
            occurred_at=row.get('occurred_at', time.time()),
            sentiment=row.get('sentiment'),
            follow_up_required=bool(row.get('follow_up_required', 0)),
            follow_up_notes=row.get('follow_up_notes'),
        )


class InteractionStore:
    """
    Interaction storage with CRUD operations.

    Uses Empirica's database infrastructure (sessions.db) with CRM tables.
    """

    def __init__(self, db_connection=None):
        """
        Initialize interaction store.

        Args:
            db_connection: SQLite connection. If None, creates one using empirica's path_resolver.
        """
        if db_connection is not None:
            self.conn = db_connection
            self._owns_connection = False
        else:
            from empirica.config.path_resolver import get_session_db_path

            db_path = get_session_db_path()
            self.conn = sqlite3.connect(str(db_path))
            self.conn.row_factory = sqlite3.Row
            self._owns_connection = True

            # Ensure schema exists
            self._ensure_schema()

    def _ensure_schema(self):
        """Create CRM tables if they don't exist."""
        from .schema import CRM_SCHEMAS

        cursor = self.conn.cursor()
        for schema in CRM_SCHEMAS:
            try:
                cursor.execute(schema)
            except Exception as e:
                logger.debug(f"Schema execution note: {e}")
        self.conn.commit()

    def log(
        self,
        client_id: str,
        summary: str,
        interaction_type: str = "email",
        engagement_id: Optional[str] = None,
        session_id: Optional[str] = None,
        contacts_involved: Optional[List[str]] = None,
        ai_id: Optional[str] = None,
        sentiment: Optional[str] = None,
        follow_up_required: bool = False,
        follow_up_notes: Optional[str] = None,
    ) -> Interaction:
        """
        Log a new interaction.

        Args:
            client_id: Client ID (required)
            summary: Summary of what happened (required)
            interaction_type: email, call, meeting, demo, document, note
            engagement_id: Optional linked engagement
            session_id: Optional Empirica session ID
            contacts_involved: List of contact names involved
            ai_id: AI identifier if AI-assisted
            sentiment: positive, neutral, negative
            follow_up_required: Whether follow-up is needed
            follow_up_notes: Notes about follow-up

        Returns:
            Interaction: Created interaction object
        """
        interaction_id = str(uuid.uuid4())
        occurred_at = time.time()

        contacts_json = json.dumps(contacts_involved) if contacts_involved else None

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO client_interactions (
                interaction_id, client_id, engagement_id, session_id,
                interaction_type, summary, contacts_involved, ai_id,
                occurred_at, sentiment, follow_up_required, follow_up_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction_id,
            client_id,
            engagement_id,
            session_id,
            interaction_type,
            summary,
            contacts_json,
            ai_id,
            occurred_at,
            sentiment,
            1 if follow_up_required else 0,
            follow_up_notes,
        ))
        self.conn.commit()

        # Update client's last_contact_at
        cursor.execute(
            "UPDATE clients SET last_contact_at = ? WHERE client_id = ?",
            (occurred_at, client_id)
        )
        self.conn.commit()

        logger.info(f"✓ Logged interaction: {summary[:50]}... ({interaction_id[:8]})")

        return Interaction(
            interaction_id=interaction_id,
            client_id=client_id,
            summary=summary,
            interaction_type=interaction_type,
            engagement_id=engagement_id,
            session_id=session_id,
            contacts_involved=contacts_involved,
            ai_id=ai_id,
            occurred_at=occurred_at,
            sentiment=sentiment,
            follow_up_required=follow_up_required,
            follow_up_notes=follow_up_notes,
        )

    def get(self, interaction_id: str) -> Optional[Interaction]:
        """Get interaction by ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM client_interactions WHERE interaction_id = ?",
            (interaction_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return Interaction.from_row(dict(row))

    def list(
        self,
        client_id: Optional[str] = None,
        engagement_id: Optional[str] = None,
        interaction_type: Optional[str] = None,
        follow_up_only: bool = False,
        limit: int = 50,
    ) -> List[Interaction]:
        """
        List interactions with optional filtering.

        Args:
            client_id: Filter by client
            engagement_id: Filter by engagement
            interaction_type: Filter by type
            follow_up_only: Only show interactions needing follow-up
            limit: Maximum number to return

        Returns:
            List of Interaction objects (most recent first)
        """
        query = "SELECT * FROM client_interactions WHERE 1=1"
        params = []

        if client_id:
            query += " AND client_id = ?"
            params.append(client_id)

        if engagement_id:
            query += " AND engagement_id = ?"
            params.append(engagement_id)

        if interaction_type:
            query += " AND interaction_type = ?"
            params.append(interaction_type)

        if follow_up_only:
            query += " AND follow_up_required = 1"

        query += " ORDER BY occurred_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [Interaction.from_row(dict(row)) for row in rows]

    def list_recent(self, client_id: str, days: int = 30) -> List[Interaction]:
        """List recent interactions for a client within specified days."""
        cutoff = time.time() - (days * 86400)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM client_interactions
            WHERE client_id = ? AND occurred_at >= ?
            ORDER BY occurred_at DESC
        """, (client_id, cutoff))
        rows = cursor.fetchall()

        return [Interaction.from_row(dict(row)) for row in rows]

    def mark_follow_up_done(self, interaction_id: str) -> Optional[Interaction]:
        """Mark an interaction's follow-up as completed."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE client_interactions
            SET follow_up_required = 0
            WHERE interaction_id = ?
        """, (interaction_id,))
        self.conn.commit()

        return self.get(interaction_id)

    def get_pending_follow_ups(self, client_id: Optional[str] = None) -> List[Interaction]:
        """Get all interactions with pending follow-ups."""
        return self.list(client_id=client_id, follow_up_only=True)

    def get_client_activity_stats(self, client_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get activity statistics for a client.

        Returns counts by interaction type and overall engagement frequency.
        """
        cutoff = time.time() - (days * 86400)

        cursor = self.conn.cursor()

        # Count by type
        cursor.execute("""
            SELECT interaction_type, COUNT(*) as count
            FROM client_interactions
            WHERE client_id = ? AND occurred_at >= ?
            GROUP BY interaction_type
        """, (client_id, cutoff))
        type_counts = {row['interaction_type']: row['count'] for row in cursor.fetchall()}

        # Total count
        total = sum(type_counts.values())

        # Sentiment breakdown
        cursor.execute("""
            SELECT sentiment, COUNT(*) as count
            FROM client_interactions
            WHERE client_id = ? AND occurred_at >= ? AND sentiment IS NOT NULL
            GROUP BY sentiment
        """, (client_id, cutoff))
        sentiment_counts = {row['sentiment']: row['count'] for row in cursor.fetchall()}

        # Calculate engagement frequency (interactions per week)
        weeks = days / 7
        frequency = total / weeks if weeks > 0 else 0

        return {
            "total_interactions": total,
            "by_type": type_counts,
            "by_sentiment": sentiment_counts,
            "engagement_frequency": round(frequency, 2),
            "period_days": days,
        }

    def close(self):
        """Close database connection if we own it."""
        if self._owns_connection and self.conn:
            self.conn.close()


# Convenience functions
def log_interaction(**kwargs) -> Interaction:
    """Log a new interaction."""
    store = InteractionStore()
    try:
        return store.log(**kwargs)
    finally:
        store.close()


def get_interaction(interaction_id: str) -> Optional[Interaction]:
    """Get interaction by ID."""
    store = InteractionStore()
    try:
        return store.get(interaction_id)
    finally:
        store.close()


def list_interactions(**kwargs) -> List[Interaction]:
    """List interactions with optional filtering."""
    store = InteractionStore()
    try:
        return store.list(**kwargs)
    finally:
        store.close()


def get_pending_follow_ups(client_id: Optional[str] = None) -> List[Interaction]:
    """Get all interactions with pending follow-ups."""
    store = InteractionStore()
    try:
        return store.get_pending_follow_ups(client_id)
    finally:
        store.close()
