"""
Notification tools registry for MCP server.

Provides email (SendGrid) and push notification (Pushover) capabilities.
"""

import json

from mcp.server.fastmcp import FastMCP

from notification_mcp_server.utils.sendgrid_client import SendGridClient
from notification_mcp_server.utils.pushover_client import PushoverClient


class NotificationTools:
    """
    Register notification tools with MCP server.

    Provides:
    - Email: Send emails via SendGrid API
    - Push: Send push notifications via Pushover API
    """

    def __init__(
        self,
        mcp: FastMCP,
        sendgrid_api_key: str | None = None,
        sendgrid_from_email: str | None = None,
        sendgrid_from_name: str | None = None,
        pushover_token: str | None = None,
        pushover_user: str | None = None,
        timeout: int = 30,
    ) -> None:
        """
        Initialize notification tools.

        Args:
            mcp: FastMCP server instance
            sendgrid_api_key: SendGrid API key
            sendgrid_from_email: Sender email address
            sendgrid_from_name: Sender display name
            pushover_token: Pushover application token
            pushover_user: Default Pushover user/group key
            timeout: Request timeout in seconds
        """
        self.mcp = mcp
        self.sendgrid_api_key = sendgrid_api_key
        self.sendgrid_from_email = sendgrid_from_email
        self.sendgrid_from_name = sendgrid_from_name
        self.pushover_token = pushover_token
        self.pushover_user = pushover_user
        self.timeout = timeout
        self._register_tools()

    def _get_sendgrid_client(self) -> SendGridClient:
        """Create a new SendGrid client."""
        return SendGridClient(
            api_key=self.sendgrid_api_key,
            from_email=self.sendgrid_from_email,
            from_name=self.sendgrid_from_name,
            timeout=self.timeout,
        )

    def _get_pushover_client(self) -> PushoverClient:
        """Create a new Pushover client."""
        return PushoverClient(
            token=self.pushover_token,
            default_user=self.pushover_user,
            timeout=self.timeout,
        )

    def _register_tools(self) -> None:
        """Register all notification tools with the MCP server."""

        # ============================================================
        # EMAIL TOOLS (SendGrid)
        # ============================================================

        @self.mcp.tool()
        async def send_email(
            to: str,
            subject: str,
            body: str,
            html_body: str | None = None,
            from_email: str | None = None,
            from_name: str | None = None,
        ) -> str:
            """
            Send an email via SendGrid.

            Args:
                to: Recipient email address.
                subject: Email subject line.
                body: Plain text email body.
                html_body: Optional HTML email body. If provided, recipients
                    with HTML-capable email clients will see this version.
                from_email: Optional sender email (overrides default).
                from_name: Optional sender name (overrides default).

            Returns:
                JSON response with success status and details.

            Example:
                send_email(
                    to="user@example.com",
                    subject="Meeting Reminder",
                    body="Don't forget our meeting at 3pm.",
                    html_body="<p>Don't forget our meeting at <b>3pm</b>.</p>"
                )
            """
            client = self._get_sendgrid_client()
            result = await client.send(
                to=to,
                subject=subject,
                body=body,
                html_body=html_body,
                from_email=from_email,
                from_name=from_name,
            )
            return json.dumps(result, indent=2)

        # ============================================================
        # PUSH NOTIFICATION TOOLS (Pushover)
        # ============================================================

        @self.mcp.tool()
        async def send_push(
            title: str,
            message: str,
            user_key: str | None = None,
            priority: int = 0,
            url: str | None = None,
            url_title: str | None = None,
            sound: str | None = None,
            device: str | None = None,
        ) -> str:
            """
            Send a push notification via Pushover.

            Args:
                title: Notification title (bold text at top).
                message: Notification message body.
                user_key: Pushover user/group key. If not provided,
                    uses the default from server configuration.
                priority: Message priority from -2 to 2:
                    -2: Lowest (no sound/vibration)
                    -1: Low (quiet hours respected)
                     0: Normal (default)
                     1: High (bypasses quiet hours)
                     2: Emergency (requires acknowledgment)
                url: Optional URL to include with message.
                url_title: Title for the URL (shows as link text).
                sound: Notification sound name. Options include:
                    pushover, bike, bugle, cashregister, classical,
                    cosmic, falling, gamelan, incoming, intermission,
                    magic, mechanical, pianobar, siren, spacealarm,
                    tugboat, alien, climb, persistent, echo, updown, none
                device: Specific device name to send to (optional).

            Returns:
                JSON response with success status and details.

            Example:
                send_push(
                    title="Server Alert",
                    message="CPU usage exceeded 90%",
                    priority=1,
                    sound="siren"
                )
            """
            client = self._get_pushover_client()
            result = await client.send(
                title=title,
                message=message,
                user_key=user_key,
                priority=priority,
                url=url,
                url_title=url_title,
                sound=sound,
                device=device,
            )
            return json.dumps(result, indent=2)

        @self.mcp.tool()
        async def validate_pushover_user(user_key: str, device: str | None = None) -> str:
            """
            Validate a Pushover user or group key.

            Use this tool to verify a user key is valid before sending
            notifications.

            Args:
                user_key: The user or group key to validate.
                device: Optional device name to validate.

            Returns:
                JSON response with validation result. Includes:
                - status: 1 for valid, 0 for invalid
                - devices: List of registered devices (if valid)
                - group: Group ID if this is a group key

            Example:
                validate_pushover_user(user_key="uQiRzpo4DXghDmr9QZgGZN27UU9JDR")
            """
            client = self._get_pushover_client()
            result = await client.validate_user(user_key=user_key, device=device)
            return json.dumps(result, indent=2)
