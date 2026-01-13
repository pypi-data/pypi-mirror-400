"""
Pushover Client for push notifications.

Uses Pushover Message API.
Docs: https://pushover.net/api
"""

from typing import Any

import httpx


class PushoverClient:
    """Pushover push notification client."""

    API_URL = "https://api.pushover.net/1/messages.json"
    VALIDATE_URL = "https://api.pushover.net/1/users/validate.json"

    # Valid sound options
    VALID_SOUNDS = frozenset({
        "pushover", "bike", "bugle", "cashregister", "classical",
        "cosmic", "falling", "gamelan", "incoming", "intermission",
        "magic", "mechanical", "pianobar", "siren", "spacealarm",
        "tugboat", "alien", "climb", "persistent", "echo", "updown",
        "vibrate", "none",
    })

    def __init__(
        self,
        token: str | None = None,
        default_user: str | None = None,
        timeout: int = 10,
    ) -> None:
        """
        Initialize Pushover client.

        Args:
            token: Pushover application token
            default_user: Default user/group key
            timeout: Request timeout in seconds
        """
        self.token = token
        self.default_user = default_user
        self.timeout = timeout

    async def send(
        self,
        title: str,
        message: str,
        user_key: str | None = None,
        priority: int = 0,
        url: str | None = None,
        url_title: str | None = None,
        sound: str | None = None,
        device: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a push notification via Pushover API.

        Args:
            title: Notification title
            message: Notification message body
            user_key: User/group key (uses default if not provided)
            priority: -2 (lowest) to 2 (emergency)
            url: Optional URL to include
            url_title: Title for the URL
            sound: Notification sound name
            device: Specific device to send to

        Returns:
            Dict with success status and response details
        """
        # Validate token
        if not self.token:
            return {
                "success": False,
                "error": "Pushover token not configured",
                "error_code": "MISSING_TOKEN",
            }

        # Use provided user_key or fall back to default
        recipient = user_key or self.default_user
        if not recipient:
            return {
                "success": False,
                "error": "Pushover user key not provided and no default configured",
                "error_code": "MISSING_USER_KEY",
            }

        # Validate priority
        if priority < -2 or priority > 2:
            return {
                "success": False,
                "error": f"Invalid priority {priority}. Must be -2 to 2.",
                "error_code": "INVALID_PRIORITY",
            }

        # Build payload (Pushover uses form data, not JSON)
        payload: dict[str, Any] = {
            "token": self.token,
            "user": recipient,
            "title": title,
            "message": message,
            "priority": priority,
        }

        # Add optional parameters
        if url:
            payload["url"] = url
        if url_title:
            payload["url_title"] = url_title
        if sound:
            if sound not in self.VALID_SOUNDS:
                return {
                    "success": False,
                    "error": f"Invalid sound '{sound}'. Valid options: {', '.join(sorted(self.VALID_SOUNDS))}",
                    "error_code": "INVALID_SOUND",
                }
            payload["sound"] = sound
        if device:
            payload["device"] = device

        # Emergency priority requires retry and expire parameters
        if priority == 2:
            payload["retry"] = 60  # Retry every 60 seconds
            payload["expire"] = 3600  # Expire after 1 hour

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.API_URL,
                    data=payload,  # Pushover uses form data
                    timeout=float(self.timeout),
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == 1:
                        return {
                            "success": True,
                            "message": "Push notification sent successfully",
                            "title": title,
                            "recipient": recipient[:10] + "...",  # Mask user key
                            "request_id": result.get("request"),
                        }
                    else:
                        errors = result.get("errors", ["Unknown error"])
                        return {
                            "success": False,
                            "error": f"Pushover error: {', '.join(errors)}",
                            "error_code": "API_ERROR",
                        }
                else:
                    try:
                        error_data = response.json()
                        errors = error_data.get("errors", [response.text])
                    except Exception:
                        errors = [response.text[:500]]

                    return {
                        "success": False,
                        "error": f"Pushover HTTP error: {', '.join(errors)}",
                        "error_code": "HTTP_ERROR",
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

    async def validate_user(
        self,
        user_key: str,
        device: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate a Pushover user or group key.

        Args:
            user_key: User or group key to validate
            device: Optional device name to validate

        Returns:
            Dict with validation result
        """
        if not self.token:
            return {
                "success": False,
                "error": "Pushover token not configured",
                "error_code": "MISSING_TOKEN",
            }

        payload: dict[str, str] = {
            "token": self.token,
            "user": user_key,
        }
        if device:
            payload["device"] = device

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.VALIDATE_URL,
                    data=payload,
                    timeout=float(self.timeout),
                )

                result = response.json()
                if result.get("status") == 1:
                    return {
                        "success": True,
                        "valid": True,
                        "devices": result.get("devices", []),
                        "group": result.get("group"),
                    }
                else:
                    return {
                        "success": True,
                        "valid": False,
                        "errors": result.get("errors", ["Invalid user key"]),
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
