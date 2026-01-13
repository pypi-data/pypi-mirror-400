# Notification MCP Server

An MCP (Model Context Protocol) server for sending notifications via **SendGrid** (email) and **Pushover** (push notifications).

## Features

- **Email via SendGrid**: Send plain text and HTML emails
- **Push Notifications via Pushover**: Send to mobile devices with priority levels, custom sounds, and URL attachments
- **User Validation**: Validate Pushover user/group keys before sending

## Installation

```bash
# Using uv (recommended)
uv pip install notification-mcp-server

# Using pip
pip install notification-mcp-server
```

## Configuration

Set the following environment variables:

### SendGrid (Email)
- `SENDGRID_API_KEY` - Your SendGrid API key (required for email)
- `SENDGRID_FROM_EMAIL` - Default sender email address
- `SENDGRID_FROM_NAME` - Default sender name (optional)

### Pushover (Push Notifications)
- `PUSHOVER_TOKEN` - Your Pushover application token (required for push)
- `PUSHOVER_USER` - Default Pushover user/group key

### General
- `NOTIFICATION_TIMEOUT` - Request timeout in seconds (default: 30)

## Usage

### As a standalone server (stdio)

```bash
notification-mcp-server
```

### With HTTP transport

```bash
notification-mcp-server --transport streamable-http --port 8000
```

### MCP Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "notification": {
      "command": "notification-mcp-server",
      "env": {
        "SENDGRID_API_KEY": "your-sendgrid-api-key",
        "SENDGRID_FROM_EMAIL": "noreply@yourdomain.com",
        "PUSHOVER_TOKEN": "your-pushover-token",
        "PUSHOVER_USER": "your-pushover-user-key"
      }
    }
  }
}
```

Or with uvx:

```json
{
  "mcpServers": {
    "notification": {
      "command": "uvx",
      "args": ["notification-mcp-server"],
      "env": {
        "SENDGRID_API_KEY": "your-sendgrid-api-key",
        "SENDGRID_FROM_EMAIL": "noreply@yourdomain.com",
        "PUSHOVER_TOKEN": "your-pushover-token",
        "PUSHOVER_USER": "your-pushover-user-key"
      }
    }
  }
}
```

## Available Tools

### send_email

Send an email via SendGrid.

**Parameters:**
- `to` (required): Recipient email address
- `subject` (required): Email subject line
- `body` (required): Plain text email body
- `html_body` (optional): HTML email body
- `from_email` (optional): Override sender email
- `from_name` (optional): Override sender name

**Example:**
```
send_email(
    to="user@example.com",
    subject="Meeting Reminder",
    body="Don't forget our meeting at 3pm.",
    html_body="<p>Don't forget our meeting at <b>3pm</b>.</p>"
)
```

### send_push

Send a push notification via Pushover.

**Parameters:**
- `title` (required): Notification title
- `message` (required): Notification message body
- `user_key` (optional): Pushover user/group key (uses default if not provided)
- `priority` (optional): -2 to 2 (default: 0)
  - -2: Lowest (no sound/vibration)
  - -1: Low (quiet hours respected)
  - 0: Normal
  - 1: High (bypasses quiet hours)
  - 2: Emergency (requires acknowledgment)
- `url` (optional): URL to include with message
- `url_title` (optional): Title for the URL
- `sound` (optional): Notification sound
- `device` (optional): Specific device name

**Example:**
```
send_push(
    title="Server Alert",
    message="CPU usage exceeded 90%",
    priority=1,
    sound="siren"
)
```

### validate_pushover_user

Validate a Pushover user or group key.

**Parameters:**
- `user_key` (required): User or group key to validate
- `device` (optional): Device name to validate

**Example:**
```
validate_pushover_user(user_key="uQiRzpo4DXghDmr9QZgGZN27UU9JDR")
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/notification-mcp-server.git
cd notification-mcp-server

# Install dependencies with uv
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .
```

## License

MIT
