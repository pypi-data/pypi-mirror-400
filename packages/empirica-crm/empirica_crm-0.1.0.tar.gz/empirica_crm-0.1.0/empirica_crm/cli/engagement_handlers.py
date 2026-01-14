"""
Engagement Command Handlers

CRUD operations for time-bounded client engagements.
"""

import json
import logging

from ._utils import _print_header

logger = logging.getLogger(__name__)


def handle_engagement_create(args):
    """Create a new engagement."""
    try:
        from empirica_crm.engagement_store import EngagementStore

        store = EngagementStore()
        try:
            engagement = store.create(
                client_id=args.client_id,
                title=args.title,
                description=getattr(args, 'description', None),
                engagement_type=getattr(args, 'engagement_type', 'outreach'),
                goal_id=getattr(args, 'goal_id', None),
                estimated_value=getattr(args, 'estimated_value', None),
                currency=getattr(args, 'currency', 'USD'),
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "engagement_id": engagement.engagement_id,
                    "client_id": engagement.client_id,
                    "title": engagement.title,
                    "message": f"Created engagement: {engagement.title}"
                }))
            else:
                _print_header(f"Engagement Created: {engagement.title}")
                print(f"\nEngagement ID: {engagement.engagement_id}")
                print(f"Client ID: {engagement.client_id}")
                print(f"Type: {engagement.engagement_type}")
                if engagement.goal_id:
                    print(f"Linked Goal: {engagement.goal_id}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_engagement_list(args):
    """List engagements with optional filtering."""
    try:
        from empirica_crm.engagement_store import EngagementStore

        store = EngagementStore()
        try:
            if getattr(args, 'goal_id', None):
                engagements = store.list_by_goal(args.goal_id)
            else:
                engagements = store.list(
                    client_id=getattr(args, 'client_id', None),
                    status=getattr(args, 'status', None),
                    engagement_type=getattr(args, 'engagement_type', None),
                    limit=getattr(args, 'limit', 50),
                )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "engagements": [e.to_dict() for e in engagements],
                    "count": len(engagements)
                }))
            else:
                _print_header("Engagements")
                if not engagements:
                    print("\nNo engagements found")
                    print("Create one with: empirica-crm engagement-create --client-id <id> --title 'Title'")
                else:
                    print(f"\nFound {len(engagements)} engagements:\n")
                    for e in engagements:
                        status_icon = {"active": "●", "completed": "✓", "stalled": "◐", "lost": "✗"}.get(e.status, "○")
                        type_label = f"[{e.engagement_type}]"
                        print(f"  {status_icon} {e.title} {type_label}")
                        print(f"     ID: {e.engagement_id[:8]}... | Client: {e.client_id[:8]}...")
                        print(f"     Active: {e.days_active} days")
                        if e.outcome:
                            print(f"     Outcome: {e.outcome}")
                        print()

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_engagement_show(args):
    """Show engagement details."""
    try:
        from empirica_crm.engagement_store import EngagementStore

        store = EngagementStore()
        try:
            engagement = store.get(args.engagement_id)

            if engagement is None:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Engagement not found"}))
                else:
                    print(f"Engagement not found: {args.engagement_id}")
                return

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": True, "engagement": engagement.to_dict()}))
            else:
                _print_header(f"Engagement: {engagement.title}")
                print(f"\nID: {engagement.engagement_id}")
                print(f"Client ID: {engagement.client_id}")
                print(f"Type: {engagement.engagement_type}")
                print(f"Status: {engagement.status}")
                print(f"Days Active: {engagement.days_active}")

                if engagement.description:
                    print(f"\nDescription: {engagement.description}")

                if engagement.goal_id:
                    print(f"\nLinked Goal: {engagement.goal_id}")

                if engagement.estimated_value:
                    print(f"\nEstimated Value: {engagement.currency} {engagement.estimated_value:,.2f}")

                if engagement.outcome:
                    print(f"\nOutcome: {engagement.outcome}")
                    if engagement.outcome_notes:
                        print(f"Notes: {engagement.outcome_notes}")
                    if engagement.actual_value:
                        print(f"Actual Value: {engagement.currency} {engagement.actual_value:,.2f}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_engagement_update(args):
    """Update engagement fields."""
    try:
        from empirica_crm.engagement_store import EngagementStore

        store = EngagementStore()
        try:
            engagement = store.update(
                engagement_id=args.engagement_id,
                title=getattr(args, 'title', None),
                description=getattr(args, 'description', None),
                engagement_type=getattr(args, 'engagement_type', None),
                status=getattr(args, 'status', None),
                goal_id=getattr(args, 'goal_id', None),
            )

            if engagement is None:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Engagement not found"}))
                else:
                    print(f"Engagement not found: {args.engagement_id}")
                return

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "engagement_id": engagement.engagement_id,
                    "title": engagement.title,
                    "message": f"Updated engagement: {engagement.title}"
                }))
            else:
                print(f"Updated engagement: {engagement.title}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_engagement_complete(args):
    """Complete an engagement with outcome."""
    try:
        from empirica_crm.engagement_store import EngagementStore

        store = EngagementStore()
        try:
            engagement = store.complete(
                engagement_id=args.engagement_id,
                outcome=args.outcome,
                outcome_notes=getattr(args, 'notes', None),
                actual_value=getattr(args, 'actual_value', None),
            )

            if engagement is None:
                if getattr(args, 'output', 'json') == 'json':
                    print(json.dumps({"ok": False, "error": "Engagement not found"}))
                else:
                    print(f"Engagement not found: {args.engagement_id}")
                return

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "engagement_id": engagement.engagement_id,
                    "title": engagement.title,
                    "outcome": engagement.outcome,
                    "message": f"Completed engagement: {engagement.title} ({engagement.outcome})"
                }))
            else:
                _print_header(f"Engagement Completed: {engagement.title}")
                print(f"\nOutcome: {engagement.outcome}")
                print(f"Days Active: {engagement.days_active}")
                if engagement.actual_value:
                    print(f"Actual Value: {engagement.currency} {engagement.actual_value:,.2f}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")
