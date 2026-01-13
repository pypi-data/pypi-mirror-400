"""
SendGrid Client for email delivery.

Uses SendGrid v3 Mail Send API.
Docs: https://docs.sendgrid.com/api-reference/mail-send/mail-send
"""

from typing import Any

import httpx


class SendGridClient:
    """SendGrid email client using v3 API."""

    API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        timeout: int = 30,
    ) -> None:
        """
        Initialize SendGrid client.

        Args:
            api_key: SendGrid API key
            from_email: Default sender email address
            from_name: Default sender name
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
        self.timeout = timeout

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Send an email via SendGrid API.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            from_email: Optional sender email (overrides default)
            from_name: Optional sender name (overrides default)

        Returns:
            Dict with success status and message details
        """
        # Validate API key
        if not self.api_key:
            return {
                "success": False,
                "error": "SendGrid API key not configured",
                "error_code": "MISSING_API_KEY",
            }

        # Use provided values or fall back to defaults
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name

        if not sender_email:
            return {
                "success": False,
                "error": "Sender email address not configured",
                "error_code": "MISSING_FROM_EMAIL",
            }

        # Build email content
        content: list[dict[str, str]] = [{"type": "text/plain", "value": body}]
        if html_body:
            content.append({"type": "text/html", "value": html_body})

        # Build payload
        payload: dict[str, Any] = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": sender_email},
            "subject": subject,
            "content": content,
        }

        # Add sender name if provided
        if sender_name:
            payload["from"]["name"] = sender_name

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=float(self.timeout),
                )

                # SendGrid returns 202 for success (accepted)
                if response.status_code in (200, 201, 202):
                    return {
                        "success": True,
                        "message": "Email sent successfully",
                        "to": to,
                        "subject": subject,
                        "status_code": response.status_code,
                    }
                else:
                    # Try to parse error response
                    try:
                        error_data = response.json()
                        errors = error_data.get("errors", [])
                        error_message = errors[0].get("message") if errors else response.text
                    except Exception:
                        error_message = response.text[:500]

                    return {
                        "success": False,
                        "error": f"SendGrid API error: {error_message}",
                        "error_code": "API_ERROR",
                        "status_code": response.status_code,
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out",
                "error_code": "TIMEOUT",
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request failed: {e!s}",
                "error_code": "REQUEST_ERROR",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e!s}",
                "error_code": "UNEXPECTED_ERROR",
            }
