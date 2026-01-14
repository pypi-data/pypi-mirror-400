"""
Empirica CRM CLI

Provides CLI commands for CRM operations. Can be used:
1. Standalone: `empirica-crm client-create --name "Company"`
2. As empirica plugin: `empirica crm client-create --name "Company"`
"""

import argparse
import json
import sys
from typing import Dict, Callable


def add_crm_parsers(subparsers):
    """Add CRM command parsers to an argparse subparsers object."""

    # CRM subcommand group
    crm_parser = subparsers.add_parser('crm', help='CRM - Client Relationship Management')
    crm_subparsers = crm_parser.add_subparsers(dest='crm_command', help='CRM commands')

    _add_client_parsers(crm_subparsers)
    _add_engagement_parsers(crm_subparsers)
    _add_interaction_parsers(crm_subparsers)
    _add_memory_parsers(crm_subparsers)
    _add_metrics_parsers(crm_subparsers)
    _add_notebook_parsers(crm_subparsers)

    return crm_parser


def _add_client_parsers(subparsers):
    """Add client management parsers."""

    # client-create
    client_create = subparsers.add_parser('client-create', help='Create a new client')
    client_create.add_argument('--name', required=True, help='Client name')
    client_create.add_argument('--description', help='Client description')
    client_create.add_argument('--notebooklm', help='NotebookLM URL for this client')
    client_create.add_argument('--type', dest='client_type', default='prospect',
                               choices=['prospect', 'active', 'partner', 'churned'],
                               help='Client type (default: prospect)')
    client_create.add_argument('--industry', help='Industry classification')
    client_create.add_argument('--contacts', help='JSON array of contacts: [{name, email, role}]')
    client_create.add_argument('--tags', help='JSON array of tags')
    client_create.add_argument('--next-action', help='Next action to take')
    client_create.add_argument('--output', choices=['human', 'json'], default='json',
                               help='Output format')

    # client-list
    client_list = subparsers.add_parser('client-list', help='List clients')
    client_list.add_argument('--status', choices=['active', 'inactive', 'archived'],
                             help='Filter by status')
    client_list.add_argument('--type', dest='client_type',
                             choices=['prospect', 'active', 'partner', 'churned'],
                             help='Filter by client type')
    client_list.add_argument('--limit', type=int, default=50, help='Max clients to show')
    client_list.add_argument('--output', choices=['human', 'json'], default='json',
                             help='Output format')

    # client-show
    client_show = subparsers.add_parser('client-show', help='Show client details')
    client_show.add_argument('--client-id', required=True, help='Client ID')
    client_show.add_argument('--include-engagements', action='store_true',
                             help='Include active engagements')
    client_show.add_argument('--output', choices=['human', 'json'], default='json',
                             help='Output format')

    # client-update
    client_update = subparsers.add_parser('client-update', help='Update client')
    client_update.add_argument('--client-id', required=True, help='Client ID')
    client_update.add_argument('--name', help='New name')
    client_update.add_argument('--description', help='New description')
    client_update.add_argument('--notebooklm', help='New NotebookLM URL')
    client_update.add_argument('--type', dest='client_type',
                               choices=['prospect', 'active', 'partner', 'churned'],
                               help='New type')
    client_update.add_argument('--industry', help='New industry')
    client_update.add_argument('--status', choices=['active', 'inactive', 'archived'],
                               help='New status')
    client_update.add_argument('--add-contact', help='Contact to add: {name, email, role}')
    client_update.add_argument('--add-tag', help='Tag to add')
    client_update.add_argument('--next-action', help='Next action')
    client_update.add_argument('--output', choices=['human', 'json'], default='json',
                               help='Output format')

    # client-archive
    client_archive = subparsers.add_parser('client-archive', help='Archive a client')
    client_archive.add_argument('--client-id', required=True, help='Client ID to archive')
    client_archive.add_argument('--output', choices=['human', 'json'], default='json',
                                help='Output format')

    # client-bootstrap
    client_bootstrap = subparsers.add_parser('client-bootstrap',
                                              help='Get client context for AI grounding')
    client_bootstrap.add_argument('--client-id', required=True, help='Client ID')
    client_bootstrap.add_argument('--output', choices=['human', 'json'], default='json',
                                  help='Output format')


def _add_engagement_parsers(subparsers):
    """Add engagement management parsers."""

    # engagement-create
    eng_create = subparsers.add_parser('engagement-create', help='Create a new engagement')
    eng_create.add_argument('--client-id', required=True, help='Client ID')
    eng_create.add_argument('--title', required=True, help='Engagement title')
    eng_create.add_argument('--description', help='Engagement description')
    eng_create.add_argument('--type', dest='engagement_type', default='outreach',
                            choices=['outreach', 'demo', 'negotiation', 'support', 'review'],
                            help='Engagement type (default: outreach)')
    eng_create.add_argument('--goal-id', help='Link to an Empirica goal')
    eng_create.add_argument('--estimated-value', type=float, help='Estimated deal value')
    eng_create.add_argument('--currency', default='USD', help='Currency (default: USD)')
    eng_create.add_argument('--output', choices=['human', 'json'], default='json',
                            help='Output format')

    # engagement-list
    eng_list = subparsers.add_parser('engagement-list', help='List engagements')
    eng_list.add_argument('--client-id', help='Filter by client')
    eng_list.add_argument('--status', choices=['active', 'completed', 'stalled', 'lost'],
                          help='Filter by status')
    eng_list.add_argument('--type', dest='engagement_type',
                          choices=['outreach', 'demo', 'negotiation', 'support', 'review'],
                          help='Filter by type')
    eng_list.add_argument('--goal-id', help='Filter by linked goal')
    eng_list.add_argument('--limit', type=int, default=50, help='Max engagements to show')
    eng_list.add_argument('--output', choices=['human', 'json'], default='json',
                          help='Output format')

    # engagement-show
    eng_show = subparsers.add_parser('engagement-show', help='Show engagement details')
    eng_show.add_argument('--engagement-id', required=True, help='Engagement ID')
    eng_show.add_argument('--output', choices=['human', 'json'], default='json',
                          help='Output format')

    # engagement-update
    eng_update = subparsers.add_parser('engagement-update', help='Update engagement')
    eng_update.add_argument('--engagement-id', required=True, help='Engagement ID')
    eng_update.add_argument('--title', help='New title')
    eng_update.add_argument('--description', help='New description')
    eng_update.add_argument('--type', dest='engagement_type',
                            choices=['outreach', 'demo', 'negotiation', 'support', 'review'],
                            help='New type')
    eng_update.add_argument('--status', choices=['active', 'completed', 'stalled', 'lost'],
                            help='New status')
    eng_update.add_argument('--goal-id', help='Link to goal')
    eng_update.add_argument('--output', choices=['human', 'json'], default='json',
                            help='Output format')

    # engagement-complete
    eng_complete = subparsers.add_parser('engagement-complete', help='Complete an engagement')
    eng_complete.add_argument('--engagement-id', required=True, help='Engagement ID')
    eng_complete.add_argument('--outcome', required=True,
                              choices=['won', 'lost', 'deferred', 'ongoing'],
                              help='Engagement outcome')
    eng_complete.add_argument('--notes', help='Outcome notes')
    eng_complete.add_argument('--actual-value', type=float, help='Actual deal value')
    eng_complete.add_argument('--output', choices=['human', 'json'], default='json',
                              help='Output format')


def _add_memory_parsers(subparsers):
    """Add client memory parsers."""

    # memory-log-finding
    mem_finding = subparsers.add_parser('memory-log-finding',
                                         help='Log a finding about a client')
    mem_finding.add_argument('--client-id', required=True, help='Client ID')
    mem_finding.add_argument('--finding', required=True, help='The finding content')
    mem_finding.add_argument('--impact', type=float, default=0.5,
                              help='Impact score 0.0-1.0 (default: 0.5)')
    mem_finding.add_argument('--engagement-id', help='Link to engagement')
    mem_finding.add_argument('--session-id', help='Empirica session ID')
    mem_finding.add_argument('--tags', help='JSON array of tags')
    mem_finding.add_argument('--output', choices=['human', 'json'], default='json',
                              help='Output format')

    # memory-log-unknown
    mem_unknown = subparsers.add_parser('memory-log-unknown',
                                         help='Log an unknown about a client')
    mem_unknown.add_argument('--client-id', required=True, help='Client ID')
    mem_unknown.add_argument('--unknown', required=True, help='What we need to learn')
    mem_unknown.add_argument('--engagement-id', help='Link to engagement')
    mem_unknown.add_argument('--session-id', help='Empirica session ID')
    mem_unknown.add_argument('--tags', help='JSON array of tags')
    mem_unknown.add_argument('--output', choices=['human', 'json'], default='json',
                              help='Output format')

    # memory-search
    mem_search = subparsers.add_parser('memory-search',
                                        help='Search client memory semantically')
    mem_search.add_argument('--client-id', required=True, help='Client ID')
    mem_search.add_argument('--query', required=True, help='Search query')
    mem_search.add_argument('--type', dest='memory_type',
                             choices=['finding', 'unknown', 'pattern'],
                             help='Filter by memory type')
    mem_search.add_argument('--limit', type=int, default=10, help='Max results')
    mem_search.add_argument('--output', choices=['human', 'json'], default='json',
                             help='Output format')

    # memory-context
    mem_context = subparsers.add_parser('memory-context',
                                         help='Get full client memory context')
    mem_context.add_argument('--client-id', required=True, help='Client ID')
    mem_context.add_argument('--limit', type=int, default=10, help='Max items per type')
    mem_context.add_argument('--output', choices=['human', 'json'], default='json',
                              help='Output format')


def _add_interaction_parsers(subparsers):
    """Add interaction logging parsers."""

    # interaction-log
    int_log = subparsers.add_parser('interaction-log', help='Log a client interaction')
    int_log.add_argument('--client-id', required=True, help='Client ID')
    int_log.add_argument('--summary', required=True, help='Summary of the interaction')
    int_log.add_argument('--type', dest='interaction_type', default='email',
                         choices=['email', 'call', 'meeting', 'demo', 'document', 'note'],
                         help='Interaction type (default: email)')
    int_log.add_argument('--engagement-id', help='Link to engagement')
    int_log.add_argument('--session-id', help='Empirica session ID')
    int_log.add_argument('--contacts', help='JSON array of contact names involved')
    int_log.add_argument('--sentiment', choices=['positive', 'neutral', 'negative'],
                         help='Interaction sentiment')
    int_log.add_argument('--follow-up', action='store_true', help='Mark as needing follow-up')
    int_log.add_argument('--follow-up-notes', help='Notes about required follow-up')
    int_log.add_argument('--output', choices=['human', 'json'], default='json',
                         help='Output format')

    # interaction-list
    int_list = subparsers.add_parser('interaction-list', help='List interactions')
    int_list.add_argument('--client-id', help='Filter by client')
    int_list.add_argument('--engagement-id', help='Filter by engagement')
    int_list.add_argument('--type', dest='interaction_type',
                          choices=['email', 'call', 'meeting', 'demo', 'document', 'note'],
                          help='Filter by type')
    int_list.add_argument('--follow-up-only', action='store_true',
                          help='Only show interactions needing follow-up')
    int_list.add_argument('--limit', type=int, default=50, help='Max interactions to show')
    int_list.add_argument('--output', choices=['human', 'json'], default='json',
                          help='Output format')

    # interaction-follow-ups
    int_followups = subparsers.add_parser('interaction-follow-ups',
                                           help='List pending follow-ups')
    int_followups.add_argument('--client-id', help='Filter by client')
    int_followups.add_argument('--output', choices=['human', 'json'], default='json',
                               help='Output format')

    # interaction-stats
    int_stats = subparsers.add_parser('interaction-stats',
                                       help='Get client activity statistics')
    int_stats.add_argument('--client-id', required=True, help='Client ID')
    int_stats.add_argument('--days', type=int, default=30,
                           help='Number of days to analyze (default: 30)')
    int_stats.add_argument('--output', choices=['human', 'json'], default='json',
                           help='Output format')


def _add_metrics_parsers(subparsers):
    """Add epistemic metrics parsers."""

    # metrics-compute
    metrics_compute = subparsers.add_parser('metrics-compute',
                                             help='Compute all epistemic metrics for a client')
    metrics_compute.add_argument('--client-id', required=True, help='Client ID')
    metrics_compute.add_argument('--days', type=int, default=30,
                                  help='Days for health calculation (default: 30)')
    metrics_compute.add_argument('--update', action='store_true',
                                  help='Update client record with computed values')
    metrics_compute.add_argument('--output', choices=['human', 'json'], default='json',
                                  help='Output format')

    # metrics-health
    metrics_health = subparsers.add_parser('metrics-health',
                                            help='Compute relationship health score')
    metrics_health.add_argument('--client-id', required=True, help='Client ID')
    metrics_health.add_argument('--days', type=int, default=30,
                                 help='Days to analyze (default: 30)')
    metrics_health.add_argument('--output', choices=['human', 'json'], default='json',
                                 help='Output format')

    # metrics-depth
    metrics_depth = subparsers.add_parser('metrics-depth',
                                           help='Compute knowledge depth score')
    metrics_depth.add_argument('--client-id', required=True, help='Client ID')
    metrics_depth.add_argument('--output', choices=['human', 'json'], default='json',
                                help='Output format')

    # client-state
    client_state = subparsers.add_parser('client-state',
                                          help='Get full epistemic state for AI grounding')
    client_state.add_argument('--client-id', required=True, help='Client ID')
    client_state.add_argument('--output', choices=['human', 'json'], default='json',
                               help='Output format')


def _add_notebook_parsers(subparsers):
    """Add NotebookLM integration parsers."""

    # notebook-info
    nb_info = subparsers.add_parser('notebook-info',
                                     help='Get NotebookLM info for a client')
    nb_info.add_argument('--client-id', required=True, help='Client ID')
    nb_info.add_argument('--output', choices=['human', 'json'], default='json',
                          help='Output format')

    # notebook-set
    nb_set = subparsers.add_parser('notebook-set',
                                    help='Set NotebookLM URL for a client')
    nb_set.add_argument('--client-id', required=True, help='Client ID')
    nb_set.add_argument('--url', required=True, help='NotebookLM URL')
    nb_set.add_argument('--output', choices=['human', 'json'], default='json',
                         help='Output format')

    # notebook-list
    nb_list = subparsers.add_parser('notebook-list',
                                     help='List clients with NotebookLM configured')
    nb_list.add_argument('--output', choices=['human', 'json'], default='json',
                          help='Output format')

    # grounding-prompt
    grounding = subparsers.add_parser('grounding-prompt',
                                       help='Get AI grounding prompt for a client')
    grounding.add_argument('--client-id', required=True, help='Client ID')
    grounding.add_argument('--output', choices=['human', 'json'], default='json',
                            help='Output format')


def get_command_handlers() -> Dict[str, Callable]:
    """Return mapping of command names to handler functions."""
    return {
        'crm': handle_crm_command,
    }


def handle_crm_command(args):
    """Route CRM subcommands to appropriate handlers."""
    from .commands import (
        handle_client_create,
        handle_client_list,
        handle_client_show,
        handle_client_update,
        handle_client_archive,
        handle_client_bootstrap,
        handle_engagement_create,
        handle_engagement_list,
        handle_engagement_show,
        handle_engagement_update,
        handle_engagement_complete,
        handle_interaction_log,
        handle_interaction_list,
        handle_interaction_follow_ups,
        handle_interaction_stats,
        handle_memory_log_finding,
        handle_memory_log_unknown,
        handle_memory_search,
        handle_memory_context,
        handle_metrics_compute,
        handle_metrics_health,
        handle_metrics_depth,
        handle_client_state,
        handle_notebook_info,
        handle_notebook_set,
        handle_notebook_list,
        handle_grounding_prompt,
    )

    crm_command = getattr(args, 'crm_command', None)

    if not crm_command:
        print("Usage: empirica-crm <command>")
        print("\nClient Commands:")
        print("  client-create     Create a new client")
        print("  client-list       List clients")
        print("  client-show       Show client details")
        print("  client-update     Update client")
        print("  client-archive    Archive a client")
        print("  client-bootstrap  Get client context for AI grounding")
        print("\nEngagement Commands:")
        print("  engagement-create   Create a new engagement")
        print("  engagement-list     List engagements")
        print("  engagement-show     Show engagement details")
        print("  engagement-update   Update engagement")
        print("  engagement-complete Complete an engagement with outcome")
        print("\nInteraction Commands:")
        print("  interaction-log       Log a client interaction")
        print("  interaction-list      List interactions")
        print("  interaction-follow-ups List pending follow-ups")
        print("  interaction-stats     Get client activity statistics")
        print("\nMemory Commands (Qdrant):")
        print("  memory-log-finding  Log a finding about a client")
        print("  memory-log-unknown  Log an unknown about a client")
        print("  memory-search       Search client memory semantically")
        print("  memory-context      Get full client memory context")
        print("\nMetrics Commands:")
        print("  metrics-compute     Compute all epistemic metrics")
        print("  metrics-health      Compute relationship health score")
        print("  metrics-depth       Compute knowledge depth score")
        print("  client-state        Get full epistemic state for AI grounding")
        print("\nNotebookLM Commands:")
        print("  notebook-info       Get NotebookLM info for a client")
        print("  notebook-set        Set NotebookLM URL for a client")
        print("  notebook-list       List clients with NotebookLM configured")
        print("  grounding-prompt    Get AI grounding prompt for a client")
        return

    handlers = {
        'client-create': handle_client_create,
        'client-list': handle_client_list,
        'client-show': handle_client_show,
        'client-update': handle_client_update,
        'client-archive': handle_client_archive,
        'client-bootstrap': handle_client_bootstrap,
        'engagement-create': handle_engagement_create,
        'engagement-list': handle_engagement_list,
        'engagement-show': handle_engagement_show,
        'engagement-update': handle_engagement_update,
        'engagement-complete': handle_engagement_complete,
        'interaction-log': handle_interaction_log,
        'interaction-list': handle_interaction_list,
        'interaction-follow-ups': handle_interaction_follow_ups,
        'interaction-stats': handle_interaction_stats,
        'memory-log-finding': handle_memory_log_finding,
        'memory-log-unknown': handle_memory_log_unknown,
        'memory-search': handle_memory_search,
        'memory-context': handle_memory_context,
        'metrics-compute': handle_metrics_compute,
        'metrics-health': handle_metrics_health,
        'metrics-depth': handle_metrics_depth,
        'client-state': handle_client_state,
        'notebook-info': handle_notebook_info,
        'notebook-set': handle_notebook_set,
        'notebook-list': handle_notebook_list,
        'grounding-prompt': handle_grounding_prompt,
    }

    handler = handlers.get(crm_command)
    if handler:
        handler(args)
    else:
        print(f"Unknown CRM command: {crm_command}")


def main(args=None):
    """Standalone CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='empirica-crm',
        description='Empirica CRM - Client Relationship Management'
    )

    subparsers = parser.add_subparsers(dest='crm_command', help='CRM commands')
    _add_client_parsers(subparsers)
    _add_engagement_parsers(subparsers)
    _add_interaction_parsers(subparsers)
    _add_memory_parsers(subparsers)
    _add_metrics_parsers(subparsers)
    _add_notebook_parsers(subparsers)

    parsed_args = parser.parse_args(args)

    if not parsed_args.crm_command:
        parser.print_help()
        return 1

    handle_crm_command(parsed_args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
