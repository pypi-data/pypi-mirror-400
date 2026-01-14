"""
Client Store - CRUD operations for CRM clients

Manages persistent client relationships with epistemic tracking.
Uses Empirica's database infrastructure.
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
class Client:
    """Client entity - persistent relationship with an organization/person."""
    client_id: str
    name: str
    description: Optional[str] = None
    notebooklm_url: Optional[str] = None
    knowledge_base_urls: List[str] = field(default_factory=list)
    contacts: List[Dict[str, str]] = field(default_factory=list)
    client_type: str = "prospect"  # prospect, active, partner, churned
    industry: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: Optional[float] = None
    created_by_ai_id: Optional[str] = None
    relationship_health: float = 0.5
    engagement_frequency: float = 0.0
    knowledge_depth: float = 0.0
    status: str = "active"  # active, inactive, archived
    last_contact_at: Optional[float] = None
    next_action: Optional[str] = None
    next_action_due: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Client":
        """Create Client from database row."""
        return cls(
            client_id=row['client_id'],
            name=row['name'],
            description=row.get('description'),
            notebooklm_url=row.get('notebooklm_url'),
            knowledge_base_urls=json.loads(row.get('knowledge_base_urls') or '[]'),
            contacts=json.loads(row.get('contacts') or '[]'),
            client_type=row.get('client_type', 'prospect'),
            industry=row.get('industry'),
            tags=json.loads(row.get('tags') or '[]'),
            created_at=row.get('created_at', time.time()),
            updated_at=row.get('updated_at'),
            created_by_ai_id=row.get('created_by_ai_id'),
            relationship_health=row.get('relationship_health', 0.5),
            engagement_frequency=row.get('engagement_frequency', 0.0),
            knowledge_depth=row.get('knowledge_depth', 0.0),
            status=row.get('status', 'active'),
            last_contact_at=row.get('last_contact_at'),
            next_action=row.get('next_action'),
            next_action_due=row.get('next_action_due'),
        )


class ClientStore:
    """
    Client storage with CRUD operations.

    Uses Empirica's database infrastructure (sessions.db) with CRM tables.
    """

    def __init__(self, db_connection=None):
        """
        Initialize client store.

        Args:
            db_connection: SQLite connection. If None, creates one using empirica's path_resolver.
        """
        if db_connection is not None:
            self.conn = db_connection
            self._owns_connection = False
        else:
            # Import from empirica to get the standard database path
            from empirica.config.path_resolver import get_session_db_path

            db_path = get_session_db_path()
            self.conn = sqlite3.connect(str(db_path))
            self.conn.row_factory = sqlite3.Row
            self._owns_connection = True

            # Ensure CRM schema exists
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
        name: str,
        description: Optional[str] = None,
        notebooklm_url: Optional[str] = None,
        knowledge_base_urls: Optional[List[str]] = None,
        contacts: Optional[List[Dict[str, str]]] = None,
        client_type: str = "prospect",
        industry: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ai_id: Optional[str] = None,
        next_action: Optional[str] = None,
        next_action_due: Optional[float] = None,
    ) -> Client:
        """
        Create a new client.

        Args:
            name: Client name (required)
            description: Client description
            notebooklm_url: NotebookLM URL for this client
            knowledge_base_urls: Additional knowledge base URLs
            contacts: List of contact dicts [{name, email, role, notes}]
            client_type: prospect, active, partner, churned
            industry: Industry classification
            tags: Tags for categorization
            ai_id: AI that created this client
            next_action: Next action to take
            next_action_due: Unix timestamp for next action deadline

        Returns:
            Client: Created client object
        """
        client_id = str(uuid.uuid4())
        created_at = time.time()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO clients (
                client_id, name, description, notebooklm_url, knowledge_base_urls,
                contacts, client_type, industry, tags, created_at, created_by_ai_id,
                next_action, next_action_due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            name,
            description,
            notebooklm_url,
            json.dumps(knowledge_base_urls or []),
            json.dumps(contacts or []),
            client_type,
            industry,
            json.dumps(tags or []),
            created_at,
            ai_id,
            next_action,
            next_action_due,
        ))
        self.conn.commit()

        logger.info(f"✓ Created client: {name} ({client_id[:8]})")

        return Client(
            client_id=client_id,
            name=name,
            description=description,
            notebooklm_url=notebooklm_url,
            knowledge_base_urls=knowledge_base_urls or [],
            contacts=contacts or [],
            client_type=client_type,
            industry=industry,
            tags=tags or [],
            created_at=created_at,
            created_by_ai_id=ai_id,
            next_action=next_action,
            next_action_due=next_action_due,
        )

    def get(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Client.from_row(dict(row))

    def get_by_name(self, name: str) -> Optional[Client]:
        """Get client by name (case-insensitive)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE LOWER(name) = LOWER(?)", (name,))
        row = cursor.fetchone()

        if row is None:
            return None

        return Client.from_row(dict(row))

    def list(
        self,
        status: Optional[str] = None,
        client_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Client]:
        """
        List clients with optional filtering.

        Args:
            status: Filter by status (active, inactive, archived)
            client_type: Filter by type (prospect, active, partner, churned)
            limit: Maximum number to return

        Returns:
            List of Client objects
        """
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if client_type:
            query += " AND client_type = ?"
            params.append(client_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [Client.from_row(dict(row)) for row in rows]

    def update(
        self,
        client_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        notebooklm_url: Optional[str] = None,
        client_type: Optional[str] = None,
        industry: Optional[str] = None,
        status: Optional[str] = None,
        next_action: Optional[str] = None,
        next_action_due: Optional[float] = None,
        add_contact: Optional[Dict[str, str]] = None,
        add_tag: Optional[str] = None,
        relationship_health: Optional[float] = None,
        knowledge_depth: Optional[float] = None,
    ) -> Optional[Client]:
        """
        Update client fields.

        Args:
            client_id: Client ID to update
            name: New name
            description: New description
            notebooklm_url: New NotebookLM URL
            client_type: New type
            industry: New industry
            status: New status
            next_action: New next action
            next_action_due: New next action due date
            add_contact: Contact to add
            add_tag: Tag to add
            relationship_health: New relationship health score
            knowledge_depth: New knowledge depth score

        Returns:
            Updated Client or None if not found
        """
        client = self.get(client_id)
        if client is None:
            return None

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if notebooklm_url is not None:
            updates.append("notebooklm_url = ?")
            params.append(notebooklm_url)

        if client_type is not None:
            updates.append("client_type = ?")
            params.append(client_type)

        if industry is not None:
            updates.append("industry = ?")
            params.append(industry)

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if next_action is not None:
            updates.append("next_action = ?")
            params.append(next_action)

        if next_action_due is not None:
            updates.append("next_action_due = ?")
            params.append(next_action_due)

        if relationship_health is not None:
            updates.append("relationship_health = ?")
            params.append(relationship_health)

        if knowledge_depth is not None:
            updates.append("knowledge_depth = ?")
            params.append(knowledge_depth)

        # Handle adding contact
        if add_contact is not None:
            contacts = client.contacts
            contacts.append(add_contact)
            updates.append("contacts = ?")
            params.append(json.dumps(contacts))

        # Handle adding tag
        if add_tag is not None:
            tags = client.tags
            if add_tag not in tags:
                tags.append(add_tag)
            updates.append("tags = ?")
            params.append(json.dumps(tags))

        if not updates:
            return client

        # Always update updated_at
        updates.append("updated_at = ?")
        params.append(time.time())

        params.append(client_id)

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE clients SET {', '.join(updates)} WHERE client_id = ?",
            params
        )
        self.conn.commit()

        logger.info(f"✓ Updated client: {client.name} ({client_id[:8]})")

        return self.get(client_id)

    def archive(self, client_id: str) -> bool:
        """
        Archive a client (soft delete).

        Args:
            client_id: Client ID to archive

        Returns:
            True if archived, False if not found
        """
        client = self.get(client_id)
        if client is None:
            return False

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE clients SET status = ?, updated_at = ? WHERE client_id = ?",
            ("archived", time.time(), client_id)
        )
        self.conn.commit()

        logger.info(f"✓ Archived client: {client.name} ({client_id[:8]})")
        return True

    def record_contact(self, client_id: str) -> bool:
        """
        Record that contact was made with client (updates last_contact_at).

        Args:
            client_id: Client ID

        Returns:
            True if updated, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE clients SET last_contact_at = ?, updated_at = ? WHERE client_id = ?",
            (time.time(), time.time(), client_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """Close database connection if we own it."""
        if self._owns_connection and self.conn:
            self.conn.close()


# Convenience functions for direct usage
def create_client(**kwargs) -> Client:
    """Create a new client."""
    store = ClientStore()
    try:
        return store.create(**kwargs)
    finally:
        store.close()


def get_client(client_id: str) -> Optional[Client]:
    """Get client by ID."""
    store = ClientStore()
    try:
        return store.get(client_id)
    finally:
        store.close()


def list_clients(status: Optional[str] = None, client_type: Optional[str] = None, limit: int = 50) -> List[Client]:
    """List clients with optional filtering."""
    store = ClientStore()
    try:
        return store.list(status=status, client_type=client_type, limit=limit)
    finally:
        store.close()


def update_client(client_id: str, **kwargs) -> Optional[Client]:
    """Update client fields."""
    store = ClientStore()
    try:
        return store.update(client_id, **kwargs)
    finally:
        store.close()


def archive_client(client_id: str) -> bool:
    """Archive a client."""
    store = ClientStore()
    try:
        return store.archive(client_id)
    finally:
        store.close()
