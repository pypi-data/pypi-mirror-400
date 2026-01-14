#!/usr/bin/env python3
"""
Entry point for running the Trino MCP Server.

Usage:
    uvx trino-mcp-navi          # Run without installation
    python -m trino_mcp_navi    # Run as module
"""

from trino_mcp_navi.server import main

if __name__ == "__main__":
    main()
