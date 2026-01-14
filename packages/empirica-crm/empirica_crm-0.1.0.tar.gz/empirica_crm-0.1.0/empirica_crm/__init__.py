"""
Empirica CRM - Client Relationship Management Module

A modular extension for Empirica that enables relational epistemics -
tracking what AI knows about entities (clients) separate from tasks (goals).

This package depends on empirica and extends its functionality with:
- Client management (persistent relationships)
- Engagement tracking (time-bounded interactions)
- Client memory (findings/unknowns scoped to clients)
- NotebookLM integration per client

Usage:
    # Standalone CLI
    empirica-crm client-create --name "Company" --type prospect

    # Or via empirica plugin (if registered)
    empirica crm client-create --name "Company" --type prospect
"""

__version__ = "0.1.0"

from .client_store import (
    Client,
    ClientStore,
    create_client,
    get_client,
    list_clients,
    update_client,
    archive_client,
)

from .engagement_store import (
    Engagement,
    EngagementStore,
    create_engagement,
    get_engagement,
    list_engagements,
    complete_engagement,
)

from .interaction_store import (
    Interaction,
    InteractionStore,
    log_interaction,
    get_interaction,
    list_interactions,
    get_pending_follow_ups,
)

from .client_memory import (
    log_client_finding,
    log_client_unknown,
    log_client_pattern,
    search_client_memory,
    get_client_context,
    confirm_finding,
    resolve_unknown,
    embed_client_memory,
)

from .epistemic_metrics import (
    compute_relationship_health,
    compute_knowledge_depth,
    compute_all_metrics,
    get_client_epistemic_state,
)

from .notebooklm import (
    get_client_notebook_url,
    get_client_notebook_info,
    set_client_notebook_url,
    build_notebook_query_prompt,
    get_grounding_prompt,
    list_clients_with_notebooks,
)

from .schema import ensure_schema, CRM_SCHEMAS


def register_plugin(empirica_cli):
    """
    Register CRM commands with Empirica CLI.

    Called by empirica's plugin system via entry point:
    [project.entry-points."empirica.plugins"]
    crm = "empirica_crm:register_plugin"
    """
    from .cli import add_crm_parsers, get_command_handlers

    # Add parsers to empirica's subparsers
    add_crm_parsers(empirica_cli.subparsers)

    # Register command handlers
    handlers = get_command_handlers()
    empirica_cli.command_handlers.update(handlers)

    return {
        'name': 'crm',
        'version': __version__,
        'commands': list(handlers.keys()),
    }


__all__ = [
    '__version__',
    # Client exports
    'Client',
    'ClientStore',
    'create_client',
    'get_client',
    'list_clients',
    'update_client',
    'archive_client',
    # Engagement exports
    'Engagement',
    'EngagementStore',
    'create_engagement',
    'get_engagement',
    'list_engagements',
    'complete_engagement',
    # Interaction exports
    'Interaction',
    'InteractionStore',
    'log_interaction',
    'get_interaction',
    'list_interactions',
    'get_pending_follow_ups',
    # Client Memory (Qdrant) exports
    'log_client_finding',
    'log_client_unknown',
    'log_client_pattern',
    'search_client_memory',
    'get_client_context',
    'confirm_finding',
    'resolve_unknown',
    'embed_client_memory',
    # Epistemic Metrics exports
    'compute_relationship_health',
    'compute_knowledge_depth',
    'compute_all_metrics',
    'get_client_epistemic_state',
    # NotebookLM Integration exports
    'get_client_notebook_url',
    'get_client_notebook_info',
    'set_client_notebook_url',
    'build_notebook_query_prompt',
    'get_grounding_prompt',
    'list_clients_with_notebooks',
    # Schema exports
    'ensure_schema',
    'CRM_SCHEMAS',
    'register_plugin',
]
