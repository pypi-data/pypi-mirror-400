"""
CRM Command Handlers - Facade Module

Re-exports all command handlers from domain-specific modules.
This maintains backward compatibility while keeping code organized.

Domain modules:
- client_handlers: Client CRUD operations
- engagement_handlers: Engagement lifecycle
- interaction_handlers: Interaction logging
- memory_handlers: Qdrant semantic memory
- metrics_handlers: Epistemic metrics computation
- notebook_handlers: NotebookLM integration
"""

# Client handlers
from .client_handlers import (
    handle_client_create,
    handle_client_list,
    handle_client_show,
    handle_client_update,
    handle_client_archive,
    handle_client_bootstrap,
)

# Engagement handlers
from .engagement_handlers import (
    handle_engagement_create,
    handle_engagement_list,
    handle_engagement_show,
    handle_engagement_update,
    handle_engagement_complete,
)

# Interaction handlers
from .interaction_handlers import (
    handle_interaction_log,
    handle_interaction_list,
    handle_interaction_follow_ups,
    handle_interaction_stats,
)

# Memory handlers
from .memory_handlers import (
    handle_memory_log_finding,
    handle_memory_log_unknown,
    handle_memory_search,
    handle_memory_context,
)

# Metrics handlers
from .metrics_handlers import (
    handle_metrics_compute,
    handle_metrics_health,
    handle_metrics_depth,
    handle_client_state,
)

# NotebookLM handlers
from .notebook_handlers import (
    handle_notebook_info,
    handle_notebook_set,
    handle_notebook_list,
    handle_grounding_prompt,
)

__all__ = [
    # Client
    'handle_client_create',
    'handle_client_list',
    'handle_client_show',
    'handle_client_update',
    'handle_client_archive',
    'handle_client_bootstrap',
    # Engagement
    'handle_engagement_create',
    'handle_engagement_list',
    'handle_engagement_show',
    'handle_engagement_update',
    'handle_engagement_complete',
    # Interaction
    'handle_interaction_log',
    'handle_interaction_list',
    'handle_interaction_follow_ups',
    'handle_interaction_stats',
    # Memory
    'handle_memory_log_finding',
    'handle_memory_log_unknown',
    'handle_memory_search',
    'handle_memory_context',
    # Metrics
    'handle_metrics_compute',
    'handle_metrics_health',
    'handle_metrics_depth',
    'handle_client_state',
    # NotebookLM
    'handle_notebook_info',
    'handle_notebook_set',
    'handle_notebook_list',
    'handle_grounding_prompt',
]
