"""Natural Payments MCP CLI."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="naturalpay",
        description="Natural Payments SDK",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # mcp subcommand
    mcp_parser = subparsers.add_parser("mcp", help="MCP server commands")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", help="MCP commands")

    # mcp serve
    serve_parser = mcp_subparsers.add_parser("serve", help="Run MCP server")
    serve_parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    serve_parser.add_argument(
        "--host",
        "-H",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)",
    )
    serve_parser.add_argument(
        "--api-key",
        "-k",
        help="API key (defaults to NATURAL_API_KEY env var)",
    )

    # version
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version",
    )

    args = parser.parse_args()

    if args.version:
        from naturalpay import __version__
        print(f"naturalpay {__version__}")
        return

    if args.command == "mcp":
        if args.mcp_command == "serve":
            from naturalpay.mcp import serve

            transport = args.transport
            if transport == "http":
                transport = "streamable-http"

            serve(
                transport=transport,
                host=args.host,
                port=args.port,
                api_key=args.api_key,
            )
        else:
            mcp_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
