"""
NotebookLM Integration - Client-specific knowledge base access

Enables AI to access client-specific NotebookLM notebooks for grounded knowledge.
Uses the notebooklm_url field on clients to identify which notebook to query.

This module provides helper functions for:
- Getting a client's NotebookLM URL
- Building context prompts that include NotebookLM references
- CLI commands to query client notebooks

Note: Actual NotebookLM querying happens via MCP tools (mcp__notebooklm__ask_question).
This module provides the glue between CRM clients and NotebookLM integration.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def get_client_notebook_url(client_id: str) -> Optional[str]:
    """
    Get the NotebookLM URL for a client.

    Args:
        client_id: Client UUID

    Returns:
        NotebookLM URL if configured, None otherwise
    """
    from .client_store import get_client

    client = get_client(client_id)
    if client is None:
        return None

    return client.notebooklm_url


def get_client_notebook_info(client_id: str) -> Dict[str, Any]:
    """
    Get NotebookLM info for a client including URL and knowledge base URLs.

    Args:
        client_id: Client UUID

    Returns:
        Dict with notebook info or error message
    """
    from .client_store import get_client

    client = get_client(client_id)
    if client is None:
        return {"error": f"Client {client_id} not found"}

    return {
        "client_id": client_id,
        "client_name": client.name,
        "notebooklm_url": client.notebooklm_url,
        "knowledge_base_urls": client.knowledge_base_urls,
        "has_notebook": client.notebooklm_url is not None,
    }


def set_client_notebook_url(client_id: str, url: str) -> bool:
    """
    Set or update the NotebookLM URL for a client.

    Args:
        client_id: Client UUID
        url: NotebookLM notebook URL

    Returns:
        True if successful, False otherwise
    """
    from .client_store import update_client

    result = update_client(client_id, notebooklm_url=url)
    return result is not None


def add_knowledge_base_url(client_id: str, url: str) -> bool:
    """
    Add a knowledge base URL to a client's list.

    Args:
        client_id: Client UUID
        url: Knowledge base URL to add

    Returns:
        True if successful, False otherwise
    """
    from .client_store import get_client, ClientStore

    client = get_client(client_id)
    if client is None:
        return False

    urls = client.knowledge_base_urls or []
    if url not in urls:
        urls.append(url)

    store = ClientStore()
    try:
        import json
        cursor = store.conn.cursor()
        cursor.execute(
            "UPDATE clients SET knowledge_base_urls = ? WHERE client_id = ?",
            (json.dumps(urls), client_id)
        )
        store.conn.commit()
        return True
    finally:
        store.close()


def build_notebook_query_prompt(
    client_id: str,
    question: str,
    include_context: bool = True,
) -> Dict[str, Any]:
    """
    Build a prompt for querying a client's NotebookLM with context.

    This creates a structured prompt that AI can use with the NotebookLM MCP tools.
    Includes client context to improve query relevance.

    Args:
        client_id: Client UUID
        question: The question to ask
        include_context: Whether to include client memory context

    Returns:
        Dict with notebook_url, question, and optional context
    """
    from .client_store import get_client
    from .client_memory import get_client_context

    client = get_client(client_id)
    if client is None:
        return {"error": f"Client {client_id} not found"}

    if not client.notebooklm_url:
        return {
            "error": f"No NotebookLM configured for client {client.name}",
            "client_id": client_id,
            "suggestion": "Add a NotebookLM URL using 'client-update --notebooklm <url>'"
        }

    result = {
        "client_id": client_id,
        "client_name": client.name,
        "notebook_url": client.notebooklm_url,
        "question": question,
    }

    if include_context:
        context = get_client_context(client_id, limit=5)

        # Build context summary
        context_parts = []

        if context.get("findings"):
            findings_text = "; ".join(
                f.get("content", "")[:100] for f in context["findings"][:3]
            )
            context_parts.append(f"Known facts: {findings_text}")

        if context.get("unknowns"):
            unknowns_text = "; ".join(
                u.get("content", "")[:100] for u in context["unknowns"][:2]
            )
            context_parts.append(f"Open questions: {unknowns_text}")

        result["context_summary"] = " | ".join(context_parts) if context_parts else None

    return result


def get_grounding_prompt(client_id: str) -> str:
    """
    Generate a grounding prompt for AI when working with a client.

    This creates a text prompt that tells the AI:
    - Who the client is
    - What notebook to use
    - What we know about them
    - What questions are open

    Returns:
        Formatted string prompt for AI grounding
    """
    from .epistemic_metrics import get_client_epistemic_state

    state = get_client_epistemic_state(client_id)

    if state.get("error"):
        return f"Error: {state['error']}"

    client = state["client"]
    metrics = state["metrics"]
    memory = state["memory"]
    actions = state["actions"]

    # Get notebook info
    notebook_info = get_client_notebook_info(client_id)

    lines = [
        f"## Client Context: {client['name']}",
        f"Type: {client['client_type']} | Status: {client['status']}",
        f"Relationship Health: {metrics['relationship_health']:.0%} | Knowledge Depth: {metrics['knowledge_depth']:.0%}",
        "",
    ]

    # NotebookLM section
    if notebook_info.get("notebooklm_url"):
        lines.append(f"**NotebookLM**: {notebook_info['notebooklm_url']}")
        lines.append("Use this notebook for client-specific knowledge queries.")
        lines.append("")

    # What we know
    if memory.get("top_findings"):
        lines.append("**What We Know:**")
        for f in memory["top_findings"][:3]:
            lines.append(f"- {f.get('content', '')[:80]}")
        lines.append("")

    # What we need to learn
    if memory.get("open_unknowns"):
        lines.append("**Open Questions:**")
        for u in memory["open_unknowns"][:3]:
            lines.append(f"? {u.get('content', '')[:80]}")
        lines.append("")

    # Next actions
    if actions.get("next_action"):
        lines.append(f"**Next Action:** {actions['next_action']}")

    if actions.get("pending_follow_ups"):
        lines.append(f"**Pending Follow-ups:** {len(actions['pending_follow_ups'])}")

    return "\n".join(lines)


def list_clients_with_notebooks() -> List[Dict[str, Any]]:
    """
    List all clients that have NotebookLM URLs configured.

    Returns:
        List of client dicts with notebook info
    """
    from .client_store import list_clients

    clients = list_clients(status="active", limit=100)

    result = []
    for client in clients:
        if client.notebooklm_url:
            result.append({
                "client_id": client.client_id,
                "name": client.name,
                "client_type": client.client_type,
                "notebooklm_url": client.notebooklm_url,
            })

    return result
