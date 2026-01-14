"""
Engagement Store - CRUD operations for client engagements

Engagements are time-bounded interactions with clients, optionally linked to goals.
Examples: outreach campaigns, demos, negotiations, support cases.
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
class Engagement:
    """Engagement entity - time-bounded client interaction."""
    engagement_id: str
    client_id: str
    title: str
    description: Optional[str] = None
    engagement_type: str = "outreach"  # outreach, demo, negotiation, support, review
    goal_id: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    status: str = "active"  # active, completed, stalled, lost
    outcome: Optional[str] = None  # won, lost, deferred, ongoing
    outcome_notes: Optional[str] = None
    estimated_value: Optional[float] = None
    actual_value: Optional[float] = None
    currency: str = "USD"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @property
    def days_active(self) -> int:
        """Calculate days since engagement started."""
        end = self.ended_at or time.time()
        return int((end - self.started_at) / 86400)

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Engagement":
        """Create Engagement from database row."""
        return cls(
            engagement_id=row['engagement_id'],
            client_id=row['client_id'],
            title=row['title'],
            description=row.get('description'),
            engagement_type=row.get('engagement_type', 'outreach'),
            goal_id=row.get('goal_id'),
            started_at=row.get('started_at', time.time()),
            ended_at=row.get('ended_at'),
            status=row.get('status', 'active'),
            outcome=row.get('outcome'),
            outcome_notes=row.get('outcome_notes'),
            estimated_value=row.get('estimated_value'),
            actual_value=row.get('actual_value'),
            currency=row.get('currency', 'USD'),
        )


class EngagementStore:
    """
    Engagement storage with CRUD operations.

    Uses Empirica's database infrastructure (sessions.db) with CRM tables.
    """

    def __init__(self, db_connection=None):
        """
        Initialize engagement store.

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

    def create(
        self,
        client_id: str,
        title: str,
        description: Optional[str] = None,
        engagement_type: str = "outreach",
        goal_id: Optional[str] = None,
        estimated_value: Optional[float] = None,
        currency: str = "USD",
    ) -> Engagement:
        """
        Create a new engagement.

        Args:
            client_id: Client ID (required)
            title: Engagement title (required)
            description: Engagement description
            engagement_type: outreach, demo, negotiation, support, review
            goal_id: Optional linked goal ID
            estimated_value: Estimated deal value
            currency: Currency code (default USD)

        Returns:
            Engagement: Created engagement object
        """
        engagement_id = str(uuid.uuid4())
        started_at = time.time()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO engagements (
                engagement_id, client_id, title, description, engagement_type,
                goal_id, started_at, estimated_value, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            engagement_id,
            client_id,
            title,
            description,
            engagement_type,
            goal_id,
            started_at,
            estimated_value,
            currency,
        ))
        self.conn.commit()

        logger.info(f"✓ Created engagement: {title} ({engagement_id[:8]})")

        return Engagement(
            engagement_id=engagement_id,
            client_id=client_id,
            title=title,
            description=description,
            engagement_type=engagement_type,
            goal_id=goal_id,
            started_at=started_at,
            estimated_value=estimated_value,
            currency=currency,
        )

    def get(self, engagement_id: str) -> Optional[Engagement]:
        """Get engagement by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM engagements WHERE engagement_id = ?", (engagement_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Engagement.from_row(dict(row))

    def list(
        self,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        engagement_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Engagement]:
        """
        List engagements with optional filtering.

        Args:
            client_id: Filter by client
            status: Filter by status (active, completed, stalled, lost)
            engagement_type: Filter by type
            limit: Maximum number to return

        Returns:
            List of Engagement objects
        """
        query = "SELECT * FROM engagements WHERE 1=1"
        params = []

        if client_id:
            query += " AND client_id = ?"
            params.append(client_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        if engagement_type:
            query += " AND engagement_type = ?"
            params.append(engagement_type)

        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [Engagement.from_row(dict(row)) for row in rows]

    def list_by_goal(self, goal_id: str) -> List[Engagement]:
        """List engagements linked to a specific goal."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM engagements WHERE goal_id = ? ORDER BY started_at DESC",
            (goal_id,)
        )
        rows = cursor.fetchall()
        return [Engagement.from_row(dict(row)) for row in rows]

    def update(
        self,
        engagement_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        engagement_type: Optional[str] = None,
        status: Optional[str] = None,
        outcome: Optional[str] = None,
        outcome_notes: Optional[str] = None,
        actual_value: Optional[float] = None,
        goal_id: Optional[str] = None,
    ) -> Optional[Engagement]:
        """
        Update engagement fields.

        Args:
            engagement_id: Engagement ID to update
            title: New title
            description: New description
            engagement_type: New type
            status: New status
            outcome: Outcome (won, lost, deferred, ongoing)
            outcome_notes: Notes about outcome
            actual_value: Actual deal value
            goal_id: Link to goal

        Returns:
            Updated Engagement or None if not found
        """
        engagement = self.get(engagement_id)
        if engagement is None:
            return None

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if engagement_type is not None:
            updates.append("engagement_type = ?")
            params.append(engagement_type)

        if status is not None:
            updates.append("status = ?")
            params.append(status)
            # Auto-set ended_at when completing
            if status in ('completed', 'lost'):
                updates.append("ended_at = ?")
                params.append(time.time())

        if outcome is not None:
            updates.append("outcome = ?")
            params.append(outcome)

        if outcome_notes is not None:
            updates.append("outcome_notes = ?")
            params.append(outcome_notes)

        if actual_value is not None:
            updates.append("actual_value = ?")
            params.append(actual_value)

        if goal_id is not None:
            updates.append("goal_id = ?")
            params.append(goal_id)

        if not updates:
            return engagement

        params.append(engagement_id)

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE engagements SET {', '.join(updates)} WHERE engagement_id = ?",
            params
        )
        self.conn.commit()

        logger.info(f"✓ Updated engagement: {engagement.title} ({engagement_id[:8]})")

        return self.get(engagement_id)

    def complete(
        self,
        engagement_id: str,
        outcome: str,
        outcome_notes: Optional[str] = None,
        actual_value: Optional[float] = None,
    ) -> Optional[Engagement]:
        """
        Mark engagement as completed with outcome.

        Args:
            engagement_id: Engagement ID
            outcome: won, lost, deferred
            outcome_notes: Notes about the outcome
            actual_value: Actual deal value

        Returns:
            Updated Engagement or None if not found
        """
        return self.update(
            engagement_id=engagement_id,
            status="completed",
            outcome=outcome,
            outcome_notes=outcome_notes,
            actual_value=actual_value,
        )

    def get_client_engagements(self, client_id: str, active_only: bool = True) -> List[Engagement]:
        """Get all engagements for a client."""
        if active_only:
            return self.list(client_id=client_id, status="active")
        return self.list(client_id=client_id)

    def close(self):
        """Close database connection if we own it."""
        if self._owns_connection and self.conn:
            self.conn.close()


# Convenience functions
def create_engagement(**kwargs) -> Engagement:
    """Create a new engagement."""
    store = EngagementStore()
    try:
        return store.create(**kwargs)
    finally:
        store.close()


def get_engagement(engagement_id: str) -> Optional[Engagement]:
    """Get engagement by ID."""
    store = EngagementStore()
    try:
        return store.get(engagement_id)
    finally:
        store.close()


def list_engagements(**kwargs) -> List[Engagement]:
    """List engagements with optional filtering."""
    store = EngagementStore()
    try:
        return store.list(**kwargs)
    finally:
        store.close()


def complete_engagement(engagement_id: str, outcome: str, **kwargs) -> Optional[Engagement]:
    """Mark engagement as completed."""
    store = EngagementStore()
    try:
        return store.complete(engagement_id, outcome, **kwargs)
    finally:
        store.close()
