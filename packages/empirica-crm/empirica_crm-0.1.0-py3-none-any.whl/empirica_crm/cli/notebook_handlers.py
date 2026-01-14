"""
NotebookLM Command Handlers

Integration with NotebookLM for client-specific knowledge bases.
"""

import json
import logging

from ._utils import _print_header

logger = logging.getLogger(__name__)


def handle_notebook_info(args):
    """Get NotebookLM info for a client."""
    try:
        from empirica_crm.notebooklm import get_client_notebook_info

        info = get_client_notebook_info(args.client_id)

        if info.get('error'):
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": False, "error": info['error']}))
            else:
                print(f"Error: {info['error']}")
            return

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                **info,
            }))
        else:
            _print_header(f"NotebookLM Info: {info['client_name']}")
            if info['notebooklm_url']:
                print(f"\nNotebookLM URL: {info['notebooklm_url']}")
            else:
                print(f"\nNo NotebookLM configured for this client")

            if info['knowledge_base_urls']:
                print(f"\nKnowledge Base URLs:")
                for url in info['knowledge_base_urls']:
                    print(f"  - {url}")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_notebook_set(args):
    """Set NotebookLM URL for a client."""
    try:
        from empirica_crm.notebooklm import set_client_notebook_url

        success = set_client_notebook_url(args.client_id, args.url)

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": success,
                "client_id": args.client_id,
                "notebooklm_url": args.url if success else None,
                "message": "NotebookLM URL set" if success else "Failed to set URL"
            }))
        else:
            if success:
                print(f"✓ NotebookLM URL set for client {args.client_id[:8]}...")
            else:
                print(f"Failed to set NotebookLM URL")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_notebook_list(args):
    """List clients with NotebookLM configured."""
    try:
        from empirica_crm.notebooklm import list_clients_with_notebooks

        clients = list_clients_with_notebooks()

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                "clients": clients,
                "count": len(clients),
            }))
        else:
            _print_header(f"Clients with NotebookLM ({len(clients)})")
            for c in clients:
                print(f"\n  {c['name']} ({c['client_type']})")
                print(f"    ID: {c['client_id'][:8]}...")
                print(f"    URL: {c['notebooklm_url']}")

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")


def handle_grounding_prompt(args):
    """Get AI grounding prompt for a client."""
    try:
        from empirica_crm.notebooklm import get_grounding_prompt

        prompt = get_grounding_prompt(args.client_id)

        if prompt.startswith("Error:"):
            if getattr(args, 'output', 'json') == 'json':
                print(json.dumps({"ok": False, "error": prompt}))
            else:
                print(prompt)
            return

        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({
                "ok": True,
                "client_id": args.client_id,
                "grounding_prompt": prompt,
            }))
        else:
            print(prompt)

    except Exception as e:
        if getattr(args, 'output', 'json') == 'json':
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
            print(f"Error: {e}")
