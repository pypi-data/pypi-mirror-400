"""
Shared CLI utilities for CRM command handlers.
"""

import json


def _print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}")


def output_result(args, success_data: dict, error: str = None):
    """
    Unified output handler for JSON/text modes.

    Args:
        args: Parsed arguments with 'output' attribute
        success_data: Dict to output on success
        error: Error message (if any)
    """
    is_json = getattr(args, 'output', 'json') == 'json'

    if error:
        if is_json:
            print(json.dumps({"ok": False, "error": error}))
        else:
            print(f"Error: {error}")
        return False

    if is_json:
        print(json.dumps({"ok": True, **success_data}))
    return True


def parse_json_arg(args, arg_name: str, output_mode: str = 'json'):
    """
    Parse a JSON argument safely.

    Returns:
        Tuple of (parsed_value, error_message)
    """
    value = getattr(args, arg_name, None)
    if value is None:
        return None, None

    try:
        return json.loads(value), None
    except json.JSONDecodeError:
        error = f"Invalid JSON in --{arg_name.replace('_', '-')}"
        if output_mode == 'json':
            print(json.dumps({"ok": False, "error": error}))
        else:
            print(f"Error: {error}")
        return None, error
