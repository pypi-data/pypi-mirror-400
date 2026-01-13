"""
Notification MCP Server.

An MCP server for sending notifications via SendGrid (email) and Pushover (push).
"""

import os

from mcp.server.fastmcp import FastMCP

from notification_mcp_server.tools import NotificationTools


def create_server(
    sendgrid_api_key: str | None = None,
    sendgrid_from_email: str | None = None,
    sendgrid_from_name: str | None = None,
    pushover_token: str | None = None,
    pushover_user: str | None = None,
    timeout: int = 30,
) -> FastMCP:
    """
    Create and configure the Notification MCP server.

    Args:
        sendgrid_api_key: SendGrid API key (or use SENDGRID_API_KEY env var)
        sendgrid_from_email: Sender email address (or use SENDGRID_FROM_EMAIL env var)
        sendgrid_from_name: Sender name (or use SENDGRID_FROM_NAME env var)
        pushover_token: Pushover application token (or use PUSHOVER_TOKEN env var)
        pushover_user: Pushover user/group key (or use PUSHOVER_USER env var)
        timeout: Request timeout in seconds

    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP(
        name="notification-mcp-server",
        instructions="""
Notification MCP Server - Email and Push Notifications

This server provides tools for sending notifications through:
- **SendGrid**: For email delivery
- **Pushover**: For push notifications to mobile devices

## Available Tools:

### Email (SendGrid)
- **send_email**: Send an email via SendGrid
  - Supports plain text and HTML content
  - Customizable from address and name

### Push Notifications (Pushover)
- **send_push**: Send a push notification via Pushover
  - Supports priority levels (-2 to 2)
  - Optional URL attachment
  - Optional sound customization

## Authentication:

Set environment variables:
- SENDGRID_API_KEY: Your SendGrid API key
- SENDGRID_FROM_EMAIL: Default sender email address
- SENDGRID_FROM_NAME: Default sender name (optional)
- PUSHOVER_TOKEN: Your Pushover application token
- PUSHOVER_USER: Default Pushover user/group key

## Examples:

### Send Email:
```
send_email(
    to="user@example.com",
    subject="Hello from MCP",
    body="This is a test email.",
    html_body="<h1>Hello</h1><p>This is a test email.</p>"
)
```

### Send Push Notification:
```
send_push(
    title="Alert",
    message="Server CPU usage is high!",
    priority=1
)
```
""",
    )

    # Get config from environment if not provided
    sendgrid_api_key = sendgrid_api_key or os.environ.get("SENDGRID_API_KEY")
    sendgrid_from_email = sendgrid_from_email or os.environ.get(
        "SENDGRID_FROM_EMAIL", "noreply@example.com"
    )
    sendgrid_from_name = sendgrid_from_name or os.environ.get("SENDGRID_FROM_NAME", "Notification")
    pushover_token = pushover_token or os.environ.get("PUSHOVER_TOKEN")
    pushover_user = pushover_user or os.environ.get("PUSHOVER_USER")
    timeout = int(os.environ.get("NOTIFICATION_TIMEOUT", timeout))

    # Register all notification tools
    NotificationTools(
        mcp=mcp,
        sendgrid_api_key=sendgrid_api_key,
        sendgrid_from_email=sendgrid_from_email,
        sendgrid_from_name=sendgrid_from_name,
        pushover_token=pushover_token,
        pushover_user=pushover_user,
        timeout=timeout,
    )

    return mcp


def main() -> None:
    """Entry point for the Notification MCP server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Notification MCP Server - Email and Push Notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  SENDGRID_API_KEY      SendGrid API key
  SENDGRID_FROM_EMAIL   Default sender email address
  SENDGRID_FROM_NAME    Default sender name
  PUSHOVER_TOKEN        Pushover application token
  PUSHOVER_USER         Pushover user/group key
  NOTIFICATION_TIMEOUT  Request timeout in seconds (default: 30)

Examples:
  # Run with environment variables
  export SENDGRID_API_KEY=your_api_key
  export PUSHOVER_TOKEN=your_token
  export PUSHOVER_USER=your_user_key
  notification-mcp-server

  # Run with HTTP transport
  notification-mcp-server --transport http --port 8000
        """,
    )

    parser.add_argument(
        "--sendgrid-api-key",
        help="SendGrid API key (default: SENDGRID_API_KEY env var)",
    )
    parser.add_argument(
        "--sendgrid-from-email",
        help="Sender email (default: SENDGRID_FROM_EMAIL env var)",
    )
    parser.add_argument(
        "--sendgrid-from-name",
        help="Sender name (default: SENDGRID_FROM_NAME env var)",
    )
    parser.add_argument(
        "--pushover-token",
        help="Pushover app token (default: PUSHOVER_TOKEN env var)",
    )
    parser.add_argument(
        "--pushover-user",
        help="Pushover user key (default: PUSHOVER_USER env var)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport mechanism (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP/SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE transport (default: 8000)",
    )

    args = parser.parse_args()

    server = create_server(
        sendgrid_api_key=args.sendgrid_api_key,
        sendgrid_from_email=args.sendgrid_from_email,
        sendgrid_from_name=args.sendgrid_from_name,
        pushover_token=args.pushover_token,
        pushover_user=args.pushover_user,
        timeout=args.timeout,
    )

    if args.transport == "stdio":
        server.run(transport="stdio")
    elif args.transport == "streamable-http":
        server.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        server.run(transport="sse", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
