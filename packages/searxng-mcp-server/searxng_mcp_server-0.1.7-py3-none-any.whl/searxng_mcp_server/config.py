import argparse
import os
import textwrap
from dataclasses import dataclass


@dataclass
class Config:
    searxng_url: str
    timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/143.0.0.0 Safari/537.36"
    )
    port: int | None = None

    @classmethod
    def from_env(cls, args: argparse.Namespace | None = None) -> "Config":
        """Create configuration from environment variables and command line arguments.

        Args:
            args: Optional argparse namespace with command line arguments

        Returns:
            Config instance
        """
        # Start with environment variables
        searxng_url = os.getenv("SEARXNG_URL")
        timeout = int(os.getenv("SEARXNG_TIMEOUT", "30"))
        user_agent = os.getenv(
            "SEARXNG_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/143.0.0.0 Safari/537.36",
        )
        port_str = os.getenv("MCP_PORT")
        port = int(port_str) if port_str else None

        # Override with command line arguments if provided
        if args:
            searxng_url = args.searxng_url or searxng_url
            timeout = args.timeout or timeout
            user_agent = args.user_agent or user_agent
            port = args.port or port

        if not searxng_url:
            raise ValueError(
                "SearxNG URL is required. Set SEARXNG_URL environment variable or use --searxng-url argument"
            )

        return cls(
            searxng_url=searxng_url.rstrip("/"),
            timeout=timeout,
            user_agent=user_agent,
            port=port,
        )


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="SearxNG MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Environment Variables:
              SEARXNG_URL           SearxNG instance URL (required)
              SEARXNG_TIMEOUT       Request timeout in seconds (default: 30)
              SEARXNG_USER_AGENT    Custom user agent string (default: Chrome 143.0.0.0)
              MCP_PORT              Port for HTTP server (default: stdio)
              LOG_LEVEL             Logging level (default: INFO)

            Examples:
              %(prog)s --searxng-url https://searx.be     # Use custom SearxNG instance
              %(prog)s --port 8080                        # Run with HTTP server on port 8080
              SEARXNG_URL=https://searx.be %(prog)s       # Use environment variable
            """),
    )

    # Add configuration arguments
    parser.add_argument("--searxng-url", help="SearxNG instance URL", default=None)
    parser.add_argument("--timeout", type=int, help="Request timeout in seconds", default=None)
    parser.add_argument("--user-agent", help="Custom user agent string", default=None)
    parser.add_argument("--port", type=int, help="Port for HTTP server (default: stdio transport)", default=None)

    return parser
