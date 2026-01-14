"""
Memory Command Handlers

Qdrant-backed semantic memory operations for client knowledge.
"""

import json
import logging

from ._utils import _print_header, parse_json_arg

logger = logging.getLogger(__name__)


def handle_memory_log_finding(args):
    """Log a finding about a client."""
    try:
        from empirica_crm.client_memory import log_client_finding

        tags, err = parse_json_arg(args, 'tags', getattr(args, 'output', 'json'))
        if err:
            return

        item_id = log_client_finding(
            client_id=args.client_id,
            finding=args.finding,
            impact=getattr(args, 'impact', 0.5),
            engagement_id=getattr(args, 'engagement_id', None),
            session_id=getattr(args, 'session_id', None),
            tags=tags,
        )

        if item_id:
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "item_id": item_id,
                    "client_id": args.client_id,
                    "memory_type": "finding",
                    "message": f"Logged finding for client {args.client_id[:8]}..."
                }))
            else:
                _print_header("Finding Logged")
                print(f"\nItem ID: {item_id}")
                print(f"Client: {args.client_id[:8]}...")
                print(f"Finding: {args.finding[:60]}...")
        else:
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": False, "error": "Failed to log finding"}))
            else:
                print("Error: Failed to log finding")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_memory_log_unknown(args):
    """Log an unknown about a client."""
    try:
        from empirica_crm.client_memory import log_client_unknown

        tags, err = parse_json_arg(args, 'tags', getattr(args, 'output', 'json'))
        if err:
            return

        item_id = log_client_unknown(
            client_id=args.client_id,
            unknown=args.unknown,
            engagement_id=getattr(args, 'engagement_id', None),
            session_id=getattr(args, 'session_id', None),
            tags=tags,
        )

        if item_id:
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({
                    "ok": True,
                    "item_id": item_id,
                    "client_id": args.client_id,
                    "memory_type": "unknown",
                    "message": f"Logged unknown for client {args.client_id[:8]}..."
                }))
            else:
                _print_header("Unknown Logged")
                print(f"\nItem ID: {item_id}")
                print(f"Client: {args.client_id[:8]}...")
                print(f"Unknown: {args.unknown[:60]}...")
        else:
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": False, "error": "Failed to log unknown"}))
            else:
                print("Error: Failed to log unknown")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_memory_search(args):
    """Search client memory semantically."""
    try:
        from empirica_crm.client_memory import search_client_memory

        results = search_client_memory(
            client_id=args.client_id,
            query=args.query,
            memory_type=getattr(args, 'memory_type', None),
            limit=getattr(args, 'limit', 10),
        )

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                "results": results,
                "count": len(results),
            }))
        else:
            _print_header(f"Memory Search: {args.query[:30]}...")
            if not results:
                print("\nNo matching memories found")
            else:
                print(f"\nFound {len(results)} memories:\n")
                for r in results:
                    score_pct = int(r.get('score', 0) * 100)
                    mem_type = r.get('memory_type', 'unknown')
                    print(f"  [{mem_type}] ({score_pct}% match)")
                    print(f"     {r.get('content', '')[:60]}...")
                    print()

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_memory_context(args):
    """Get full client memory context."""
    try:
        from empirica_crm.client_memory import get_client_context

        context = get_client_context(
            client_id=args.client_id,
            limit=getattr(args, 'limit', 10),
        )

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                "client_id": args.client_id,
                "context": context,
            }))
        else:
            _print_header(f"Client Memory Context")
            print(f"\nClient: {args.client_id[:8]}...")

            if context.get('findings'):
                print(f"\nFindings ({len(context['findings'])}):")
                for f in context['findings'][:5]:
                    print(f"  - {f.get('content', '')[:60]}...")

            if context.get('unknowns'):
                print(f"\nUnknowns ({len(context['unknowns'])}):")
                for u in context['unknowns'][:5]:
                    print(f"  ? {u.get('content', '')[:60]}...")

            if context.get('patterns'):
                print(f"\nPatterns ({len(context['patterns'])}):")
                for p in context['patterns'][:5]:
                    print(f"  ~ {p.get('content', '')[:60]}...")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")
