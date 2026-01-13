"""Entry point for S3 MCP Server."""

import sys
from .server import mcp


def main() -> int:
    """
    Run the S3 MCP server.

    This function starts the FastMCP server using stdio transport,
    allowing it to communicate with MCP clients through standard input/output.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Run the FastMCP server
        # FastMCP automatically uses stdio transport when run() is called
        mcp.run()
        return 0
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
