"""
Client Command Handlers

CRUD operations for client records.
"""

import json
import logging

from ._utils import _print_header, parse_json_arg

logger = logging.getLogger(__name__)


def handle_client_create(args):
    """Create a new client."""
    try:
        from empirica_crm import ClientStore

        contacts, err = parse_json_arg(args, 'contacts', getattr(args, 'output', 'json'))
        if err:
            return

        tags, err = parse_json_arg(args, 'tags', getattr(args, 'output', 'json'))
        if err:
            return

        store = ClientStore()
        try:
            client = store.create(
                name=args.name,
                description=getattr(args, 'description', None),
                notebooklm_url=getattr(args, 'notebooklm', None),
                contacts=contacts,
                client_type=getattr(args, 'client_type', 'prospect'),
                industry=getattr(args, 'industry', None),
                tags=tags,
                next_action=getattr(args, 'next_action', None),
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "client_id": client.client_id,
                    "name": client.name,
                    "message": f"Created client: {client.name}"
                }))
            else:
                _print_header(f"✓ Client Created: {client.name}")
                print(f"\nClient ID: {client.client_id}")
                print(f"Type: {client.client_type}")
                if client.notebooklm_url:
                    print(f"NotebookLM: {client.notebooklm_url}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_client_list(args):
    """List clients with optional filtering."""
    try:
        from empirica_crm import ClientStore

        store = ClientStore()
        try:
            clients = store.list(
                status=getattr(args, 'status', None),
                client_type=getattr(args, 'client_type', None),
                limit=getattr(args, 'limit', 50),
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "clients": [c.to_dict() for c in clients],
                    "count": len(clients)
                }))
            else:
                _print_header("Clients")
                if not clients:
                    print("\nNo clients found")
                    print("Create a client with: empirica-crm client-create --name 'Company'")
                else:
                    print(f"\nFound {len(clients)} clients:\n")
                    for c in clients:
                        status_icon = "●" if c.status == "active" else "○"
                        type_label = f"[{c.client_type}]" if c.client_type else ""
                        print(f"  {status_icon} {c.name} {type_label}")
                        print(f"     ID: {c.client_id[:8]}...")
                        if c.next_action:
                            print(f"     Next: {c.next_action}")
                        print()

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_client_show(args):
    """Show client details."""
    try:
        from empirica_crm import ClientStore

        store = ClientStore()
        try:
            client = store.get(args.client_id)

            if client is None:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Client not found"}))
                else:
                    print(f"Client not found: {args.client_id}")
                return

            if getattr(args, 'output', 'json') == 'json':
                result = {"ok": True, "client": client.to_dict()}
                print(json.dumps(result))
            else:
                _print_header(f"Client: {client.name}")
                print(f"\nID: {client.client_id}")
                print(f"Type: {client.client_type}")
                print(f"Status: {client.status}")

                if client.description:
                    print(f"\nDescription: {client.description}")

                if client.industry:
                    print(f"Industry: {client.industry}")

                if client.notebooklm_url:
                    print(f"\nNotebookLM: {client.notebooklm_url}")

                if client.contacts:
                    print("\nContacts:")
                    for contact in client.contacts:
                        print(f"  - {contact.get('name', 'Unknown')}")
                        if contact.get('email'):
                            print(f"    Email: {contact['email']}")
                        if contact.get('role'):
                            print(f"    Role: {contact['role']}")

                if client.tags:
                    print(f"\nTags: {', '.join(client.tags)}")

                print(f"\nEpistemic State:")
                print(f"  Relationship Health: {client.relationship_health:.2f}")
                print(f"  Knowledge Depth: {client.knowledge_depth:.2f}")

                if client.next_action:
                    print(f"\nNext Action: {client.next_action}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_client_update(args):
    """Update client fields."""
    try:
        from empirica_crm import ClientStore

        add_contact, err = parse_json_arg(args, 'add_contact', getattr(args, 'output', 'json'))
        if err:
            return

        store = ClientStore()
        try:
            client = store.update(
                client_id=args.client_id,
                name=getattr(args, 'name', None),
                description=getattr(args, 'description', None),
                notebooklm_url=getattr(args, 'notebooklm', None),
                client_type=getattr(args, 'client_type', None),
                industry=getattr(args, 'industry', None),
                status=getattr(args, 'status', None),
                next_action=getattr(args, 'next_action', None),
                add_contact=add_contact,
                add_tag=getattr(args, 'add_tag', None),
            )

            if client is None:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Client not found"}))
                else:
                    print(f"Client not found: {args.client_id}")
                return

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "client_id": client.client_id,
                    "name": client.name,
                    "message": f"Updated client: {client.name}"
                }))
            else:
                print(f"✓ Updated client: {client.name}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_client_archive(args):
    """Archive a client (soft delete)."""
    try:
        from empirica_crm import ClientStore

        store = ClientStore()
        try:
            success = store.archive(args.client_id)

            if not success:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Client not found"}))
                else:
                    print(f"Client not found: {args.client_id}")
                return

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "client_id": args.client_id,
                    "message": "Client archived"
                }))
            else:
                print(f"✓ Archived client: {args.client_id}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_client_bootstrap(args):
    """Get client context for AI grounding."""
    try:
        from empirica_crm import ClientStore
        from empirica_crm.engagement_store import EngagementStore

        store = ClientStore()
        eng_store = EngagementStore(db_connection=store.conn)
        try:
            client = store.get(args.client_id)

            if client is None:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Client not found"}))
                else:
                    print(f"Client not found: {args.client_id}")
                return

            # Load active engagements
            active_engagements = eng_store.get_client_engagements(args.client_id, active_only=True)

            # Build bootstrap context
            bootstrap = {
                "ok": True,
                "client": {
                    "client_id": client.client_id,
                    "name": client.name,
                    "description": client.description,
                    "notebooklm_url": client.notebooklm_url,
                    "contacts": client.contacts,
                    "client_type": client.client_type,
                    "industry": client.industry,
                    "tags": client.tags,
                    "relationship_health": client.relationship_health,
                    "knowledge_depth": client.knowledge_depth,
                },
                "active_engagements": [e.to_dict() for e in active_engagements],
                "client_memory": {
                    "findings": [],
                    "unknowns": [],
                },
                "recent_interactions": [],
                "next_action": client.next_action,
            }

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps(bootstrap))
            else:
                _print_header(f"Client Bootstrap: {client.name}")
                print(f"\nClient ID: {client.client_id}")
                print(f"Type: {client.client_type}")
                print(f"Status: {client.status}")

                if client.notebooklm_url:
                    print(f"\nNotebookLM: {client.notebooklm_url}")

                print(f"\nEpistemic State:")
                print(f"  Relationship Health: {client.relationship_health:.2f}")
                print(f"  Knowledge Depth: {client.knowledge_depth:.2f}")

                if active_engagements:
                    print(f"\nActive Engagements ({len(active_engagements)}):")
                    for e in active_engagements:
                        print(f"  - {e.title} [{e.engagement_type}] ({e.days_active}d)")

                if client.next_action:
                    print(f"\nNext Action: {client.next_action}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")
