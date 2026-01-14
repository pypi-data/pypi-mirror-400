"""Entry point for Mem-Brain MCP Server."""

import logging
import sys

from mem_brain_mcp.config import settings
from mem_brain_mcp.server import run_server

def main():
    """Main entry point for the CLI."""
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr
    )

    logger = logging.getLogger(__name__)

    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
