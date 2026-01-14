"""CLI entry point for cognitive-core.

Provides a JSON-based interface for subprocess communication,
enabling language bindings (TypeScript, etc.) to interact with
the Python implementation.

Usage:
    # Interactive JSON mode (for subprocess wrappers)
    cognitive-core --json

    # Single command
    echo '{"command": "memory.search", "args": {"query": "test"}}' | cognitive-core --json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

__version__ = "0.1.0"


def handle_command(command: str, args: dict[str, Any]) -> dict[str, Any]:
    """Handle a single command and return the result.

    Args:
        command: The command to execute (e.g., "memory.search", "env.reset")
        args: Command arguments

    Returns:
        Result dictionary with "success" and either "result" or "error"
    """
    try:
        parts = command.split(".")

        if parts[0] == "version":
            return {"success": True, "result": {"version": __version__}}

        elif parts[0] == "memory":
            return _handle_memory_command(parts[1:], args)

        elif parts[0] == "env":
            return _handle_env_command(parts[1:], args)

        elif parts[0] == "search":
            return _handle_search_command(parts[1:], args)

        else:
            return {"success": False, "error": f"Unknown command: {command}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _handle_memory_command(parts: list[str], args: dict[str, Any]) -> dict[str, Any]:
    """Handle memory.* commands."""
    if not parts:
        return {"success": False, "error": "No memory subcommand specified"}

    subcommand = parts[0]

    if subcommand == "search":
        from cognitive_core.memory import MemorySystemImpl

        # This is a simplified example - real implementation would
        # maintain state across calls
        query = args.get("query", "")
        k = args.get("k", 5)

        return {
            "success": True,
            "result": {
                "message": f"Would search for: {query} (k={k})",
                "note": "Full implementation requires initialized memory system",
            },
        }

    elif subcommand == "store":
        return {
            "success": True,
            "result": {"message": "Would store trajectory"},
        }

    else:
        return {"success": False, "error": f"Unknown memory command: {subcommand}"}


def _handle_env_command(parts: list[str], args: dict[str, Any]) -> dict[str, Any]:
    """Handle env.* commands."""
    if not parts:
        return {"success": False, "error": "No env subcommand specified"}

    subcommand = parts[0]

    if subcommand == "create":
        domain = args.get("domain", "passthrough")
        return {
            "success": True,
            "result": {"env_id": f"{domain}_env_1", "domain": domain},
        }

    elif subcommand == "reset":
        env_id = args.get("env_id")
        task = args.get("task", {})
        return {
            "success": True,
            "result": {
                "env_id": env_id,
                "observation": task.get("description", "Task reset"),
            },
        }

    elif subcommand == "step":
        env_id = args.get("env_id")
        action = args.get("action", "")
        return {
            "success": True,
            "result": {
                "observation": f"Executed: {action}",
                "reward": 0.0,
                "done": False,
                "info": {},
            },
        }

    elif subcommand == "verify":
        env_id = args.get("env_id")
        solution = args.get("solution")
        return {
            "success": True,
            "result": {
                "success": True,
                "partial_score": 1.0,
                "details": {},
            },
        }

    else:
        return {"success": False, "error": f"Unknown env command: {subcommand}"}


def _handle_search_command(parts: list[str], args: dict[str, Any]) -> dict[str, Any]:
    """Handle search.* commands."""
    if not parts:
        return {"success": False, "error": "No search subcommand specified"}

    subcommand = parts[0]

    if subcommand == "solve":
        task = args.get("task", {})
        return {
            "success": True,
            "result": {
                "message": f"Would solve task: {task.get('id', 'unknown')}",
            },
        }

    else:
        return {"success": False, "error": f"Unknown search command: {subcommand}"}


def run_json_mode() -> None:
    """Run in JSON mode, reading commands from stdin."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            command = request.get("command", "")
            args = request.get("args", {})

            result = handle_command(command, args)
            print(json.dumps(result), flush=True)

        except json.JSONDecodeError as e:
            error_response = {"success": False, "error": f"Invalid JSON: {e}"}
            print(json.dumps(error_response), flush=True)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cognitive Core - Meta-learning framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get version
  cognitive-core --version

  # Run in JSON mode for subprocess communication
  cognitive-core --json

  # Pipe commands in JSON mode
  echo '{"command": "version"}' | cognitive-core --json
        """,
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"cognitive-core {__version__}"
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Run in JSON mode (for subprocess communication)",
    )

    args = parser.parse_args()

    if args.json:
        run_json_mode()
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
