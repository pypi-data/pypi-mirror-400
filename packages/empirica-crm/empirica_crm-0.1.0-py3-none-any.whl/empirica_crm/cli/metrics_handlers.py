"""
Metrics Command Handlers

Epistemic metrics computation for client relationships.
"""

import json
import logging

from ._utils import _print_header

logger = logging.getLogger(__name__)


def handle_metrics_compute(args):
    """Compute epistemic metrics for a client."""
    try:
        from empirica_crm.epistemic_metrics import compute_all_metrics

        metrics = compute_all_metrics(
            client_id=args.client_id,
            days=getattr(args, 'days', 30),
            update_client=getattr(args, 'update', False),
        )

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                **metrics,
            }))
        else:
            _print_header(f"Epistemic Metrics")
            print(f"\nClient: {args.client_id[:8]}...")
            print(f"\n  Relationship Health: {metrics['relationship_health']:.1%}")
            print(f"  Knowledge Depth:     {metrics['knowledge_depth']:.1%}")

            print(f"\nHealth Breakdown:")
            for k, v in metrics['health_breakdown'].items():
                print(f"    {k}: {v:.1%}")

            print(f"\nDepth Breakdown:")
            for k, v in metrics['depth_breakdown'].items():
                print(f"    {k}: {v:.1%}")

            if metrics.get('client_updated'):
                print(f"\n✓ Client record updated with new metrics")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_metrics_health(args):
    """Compute relationship health for a client."""
    try:
        from empirica_crm.epistemic_metrics import compute_relationship_health

        health = compute_relationship_health(
            client_id=args.client_id,
            days=getattr(args, 'days', 30),
        )

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                "client_id": args.client_id,
                **health,
            }))
        else:
            _print_header(f"Relationship Health")
            print(f"\nClient: {args.client_id[:8]}...")
            print(f"Score: {health['relationship_health']:.1%}")

            print(f"\nBreakdown:")
            for k, v in health['breakdown'].items():
                print(f"  {k}: {v:.1%}")

            print(f"\nRaw Data:")
            rd = health['raw_data']
            print(f"  Total interactions: {rd['total_interactions']}")
            print(f"  Interactions/week: {rd['interactions_per_week']}")
            print(f"  Pending follow-ups: {rd['pending_follow_ups']}")
            print(f"  Engagements won: {rd['engagements_won']}")
            print(f"  Engagements lost: {rd['engagements_lost']}")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_metrics_depth(args):
    """Compute knowledge depth for a client."""
    try:
        from empirica_crm.epistemic_metrics import compute_knowledge_depth

        depth = compute_knowledge_depth(client_id=args.client_id)

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                "client_id": args.client_id,
                **depth,
            }))
        else:
            _print_header(f"Knowledge Depth")
            print(f"\nClient: {args.client_id[:8]}...")
            print(f"Score: {depth['knowledge_depth']:.1%}")

            print(f"\nBreakdown:")
            for k, v in depth['breakdown'].items():
                print(f"  {k}: {v:.1%}")

            print(f"\nRaw Data:")
            rd = depth['raw_data']
            print(f"  Findings: {rd['finding_count']}")
            print(f"  Patterns: {rd['pattern_count']}")
            print(f"  Unknowns: {rd['unknown_count']}")
            print(f"  Avg confidence: {rd['avg_confidence']:.1%}")
            print(f"  Avg impact: {rd['avg_impact']:.1%}")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_client_state(args):
    """Get full epistemic state for client (for AI grounding)."""
    try:
        from empirica_crm.epistemic_metrics import get_client_epistemic_state

        state = get_client_epistemic_state(client_id=args.client_id)

        if state.get('error'):
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": False, "error": state['error']}))
            else:
                print(f"Error: {state['error']}")
            return

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                **state,
            }))
        else:
            client = state['client']
            metrics = state['metrics']
            memory = state['memory']
            actions = state['actions']

            _print_header(f"Client Epistemic State: {client['name']}")
            print(f"\nClient ID: {client['client_id'][:8]}...")
            print(f"Type: {client['client_type']}")
            print(f"Status: {client['status']}")

            print(f"\nMetrics:")
            print(f"  Relationship Health: {metrics['relationship_health']:.1%}")
            print(f"  Knowledge Depth: {metrics['knowledge_depth']:.1%}")

            if memory['top_findings']:
                print(f"\nTop Findings ({len(memory['top_findings'])}):")
                for f in memory['top_findings'][:3]:
                    print(f"  ✓ {f.get('content', '')[:50]}...")

            if memory['open_unknowns']:
                print(f"\nOpen Unknowns ({len(memory['open_unknowns'])}):")
                for u in memory['open_unknowns'][:3]:
                    print(f"  ? {u.get('content', '')[:50]}...")

            if actions['next_action']:
                print(f"\nNext Action: {actions['next_action']}")

            if actions['pending_follow_ups']:
                print(f"\nPending Follow-ups: {len(actions['pending_follow_ups'])}")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")
