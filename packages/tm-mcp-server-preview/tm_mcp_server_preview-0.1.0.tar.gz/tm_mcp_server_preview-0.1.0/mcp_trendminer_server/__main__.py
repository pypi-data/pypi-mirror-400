"""Entry point for running the MCP TrendMiner server."""

import sys
from pathlib import Path


def main():
    """Main entry point with first-run setup detection."""
    # Check for --setup flag
    if "--setup" in sys.argv:
        from mcp_trendminer_server.setup import run_setup
        success = run_setup()
        if success:
            print("\n💡 Setup complete! To start the server, run:")
            print("   npx @inspectr/inspectr\n")
        sys.exit(0 if success else 1)

    # Check if this is the first run (no .env file)
    if not Path(".env").exists():
        print("\n🔧 No configuration found. Starting first-time setup...\n")
        from mcp_trendminer_server.setup import run_setup

        success = run_setup()
        if not success:
            sys.exit(1)

        print("\nConfiguration complete! Starting server...\n")

    # Start the MCP server
    from mcp_trendminer_server.server import main as server_main
    server_main()


if __name__ == "__main__":
    main()
