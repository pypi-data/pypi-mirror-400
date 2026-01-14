"""
Interaction Command Handlers

Logging and querying client interactions.
"""

import json
import logging
from datetime import datetime

from ._utils import _print_header, parse_json_arg

logger = logging.getLogger(__name__)


def handle_interaction_log(args):
    """Log a client interaction."""
    try:
        from empirica_crm.interaction_store import InteractionStore

        contacts, err = parse_json_arg(args, 'contacts', getattr(args, 'output', 'json'))
        if err:
            return

        store = InteractionStore()
        try:
            interaction = store.log(
                client_id=args.client_id,
                summary=args.summary,
                interaction_type=getattr(args, 'interaction_type', 'email'),
                engagement_id=getattr(args, 'engagement_id', None),
                session_id=getattr(args, 'session_id', None),
                contacts_involved=contacts,
                sentiment=getattr(args, 'sentiment', None),
                follow_up_required=getattr(args, 'follow_up', False),
                follow_up_notes=getattr(args, 'follow_up_notes', None),
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "interaction_id": interaction.interaction_id,
                    "client_id": interaction.client_id,
                    "summary": interaction.summary,
                    "message": f"Logged interaction: {interaction.summary[:50]}..."
                }))
            else:
                _print_header(f"Interaction Logged")
                print(f"\nID: {interaction.interaction_id}")
                print(f"Type: {interaction.interaction_type}")
                print(f"Summary: {interaction.summary}")
                if interaction.follow_up_required:
                    print(f"\nFollow-up Required!")
                    if interaction.follow_up_notes:
                        print(f"Notes: {interaction.follow_up_notes}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_interaction_list(args):
    """List interactions with optional filtering."""
    try:
        from empirica_crm.interaction_store import InteractionStore

        store = InteractionStore()
        try:
            interactions = store.list(
                client_id=getattr(args, 'client_id', None),
                engagement_id=getattr(args, 'engagement_id', None),
                interaction_type=getattr(args, 'interaction_type', None),
                follow_up_only=getattr(args, 'follow_up_only', False),
                limit=getattr(args, 'limit', 50),
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "interactions": [i.to_dict() for i in interactions],
                    "count": len(interactions)
                }))
            else:
                _print_header("Interactions")
                if not interactions:
                    print("\nNo interactions found")
                    print("Log one with: empirica-crm interaction-log --client-id <id> --summary 'Summary'")
                else:
                    print(f"\nFound {len(interactions)} interactions:\n")
                    for i in interactions:
                        dt = datetime.fromtimestamp(i.occurred_at)
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                        sentiment_icon = {"positive": "+", "neutral": "~", "negative": "-"}.get(i.sentiment, " ")
                        follow_up = " [F/U]" if i.follow_up_required else ""
                        print(f"  [{i.interaction_type}] {date_str} {sentiment_icon}{follow_up}")
                        print(f"     {i.summary[:60]}...")
                        print(f"     ID: {i.interaction_id[:8]}...")
                        print()

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_interaction_follow_ups(args):
    """List pending follow-ups."""
    try:
        from empirica_crm.interaction_store import InteractionStore

        store = InteractionStore()
        try:
            interactions = store.get_pending_follow_ups(
                client_id=getattr(args, 'client_id', None)
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "follow_ups": [i.to_dict() for i in interactions],
                    "count": len(interactions)
                }))
            else:
                _print_header("Pending Follow-Ups")
                if not interactions:
                    print("\nNo pending follow-ups")
                else:
                    print(f"\n{len(interactions)} pending follow-ups:\n")
                    for i in interactions:
                        dt = datetime.fromtimestamp(i.occurred_at)
                        date_str = dt.strftime("%Y-%m-%d")
                        print(f"  [{i.interaction_type}] {date_str}")
                        print(f"     {i.summary[:60]}...")
                        if i.follow_up_notes:
                            print(f"     Notes: {i.follow_up_notes}")
                        print(f"     ID: {i.interaction_id[:8]}... | Client: {i.client_id[:8]}...")
                        print()

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_interaction_stats(args):
    """Get client activity statistics."""
    try:
        from empirica_crm.interaction_store import InteractionStore

        store = InteractionStore()
        try:
            stats = store.get_client_activity_stats(
                client_id=args.client_id,
                days=getattr(args, 'days', 30),
            )

            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": True, "stats": stats}))
            else:
                _print_header(f"Activity Stats (Last {stats['period_days']} days)")
                print(f"\nTotal Interactions: {stats['total_interactions']}")
                print(f"Engagement Frequency: {stats['engagement_frequency']}/week")

                if stats['by_type']:
                    print("\nBy Type:")
                    for t, count in stats['by_type'].items():
                        print(f"  {t}: {count}")

                if stats['by_sentiment']:
                    print("\nBy Sentiment:")
                    for s, count in stats['by_sentiment'].items():
                        print(f"  {s}: {count}")

        finally:
            store.close()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")
