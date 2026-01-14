"""CLI entrypoint for claude-code-relay."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from .cli_wrapper import ClaudeCLI, CLIConfig
from .server import run_server


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="claude-code-relay",
        description="OpenAI-compatible API server for Claude CLI",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version="claude-code-relay 0.0.1",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.getenv("CLAUDE_CODE_RELAY_PORT", "52014")),
        help="Port to listen on (default: 52014)",
    )
    serve_parser.add_argument(
        "--host",
        default=os.getenv("CLAUDE_CODE_RELAY_HOST", "127.0.0.1"),
        help="Host to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--claude-path",
        default=os.getenv("CLAUDE_CLI_PATH", "claude"),
        help="Path to Claude CLI binary",
    )
    serve_parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("CLAUDE_CODE_RELAY_TIMEOUT", "300")),
        help="Request timeout in seconds (default: 300)",
    )
    serve_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    # check command
    subparsers.add_parser("check", help="Check if Claude CLI is available")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Configure logging
    log_level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if args.command == "serve":
        config = CLIConfig(
            cli_path=args.claude_path,
            timeout=args.timeout,
            verbose=args.verbose,
        )

        print("Starting Claude Code Relay server...")
        print(f"  Host: {args.host}")
        print(f"  Port: {args.port}")
        print(f"  Claude CLI: {args.claude_path}")
        print(f"  Timeout: {args.timeout}s")
        print()
        print(f"API endpoint: http://{args.host}:{args.port}/v1/chat/completions")
        print()

        try:
            run_server(host=args.host, port=args.port, config=config)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)

    elif args.command == "check":
        print("Checking Claude CLI...")
        try:
            config = CLIConfig.from_env()
            ClaudeCLI(config)
            print(f"  CLI path: {config.cli_path}")
            print("  Status: OK")
        except RuntimeError as e:
            print(f"  Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
