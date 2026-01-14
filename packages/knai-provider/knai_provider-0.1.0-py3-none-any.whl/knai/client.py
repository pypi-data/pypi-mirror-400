"""KNAI Provider SDK client for session-based wallet charging."""

import time
from typing import Any, Dict, Optional

import requests

from .errors import (
    InsufficientBalanceError,
    InvalidAPIKeyError,
    KNAIError,
    SessionExpiredError,
)

DEFAULT_BASE_URL = "https://api.conx.ai"
DEFAULT_TIMEOUT = 30


class KNAIProvider:
    """
    Client for KNAI Wallet provider integration.

    This SDK allows AI providers to poll for active sessions and charge
    wallet usage on a per-use basis.

    Args:
        provider_api_key: Your provider API key for authentication.
        provider_slug: Your unique provider identifier.
        base_url: Optional API base URL (defaults to https://api.conx.ai).
    """

    def __init__(
        self,
        provider_api_key: str,
        provider_slug: str,
        base_url: str = DEFAULT_BASE_URL,
    ):
        if not provider_api_key:
            raise ValueError("provider_api_key is required")
        if not provider_slug:
            raise ValueError("provider_slug is required")

        self._api_key = provider_api_key
        self._provider_slug = provider_slug
        self._base_url = base_url.rstrip("/")

    def _get_headers(self, session_token: Optional[str] = None) -> Dict[str, str]:
        """Build request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "X-Provider-API-Key": self._api_key,
            "X-Provider-Slug": self._provider_slug,
        }
        if session_token:
            headers["X-Session-Token"] = session_token
        return headers

    def _handle_error_response(self, response: requests.Response) -> None:
        """Map API error responses to appropriate exceptions."""
        status_code = response.status_code

        try:
            body = response.json()
        except ValueError:
            body = {"error": response.text}

        error_message = body.get("error", body.get("message", "Unknown error"))

        if status_code == 401:
            raise InvalidAPIKeyError(
                message=error_message,
                status_code=status_code,
                response_body=body,
            )
        elif status_code == 402:
            raise InsufficientBalanceError(
                message=error_message,
                status_code=status_code,
                response_body=body,
            )
        elif status_code == 403 or status_code == 410:
            raise SessionExpiredError(
                message=error_message,
                status_code=status_code,
                response_body=body,
            )
        else:
            raise KNAIError(
                message=error_message,
                status_code=status_code,
                response_body=body,
            )

    def wait_for_session(
        self,
        provider_username: str,
        poll_interval: float = 1.5,
    ) -> Dict[str, Any]:
        """
        Poll for an active provider session.

        This method blocks until a session becomes active for the given user.

        Args:
            provider_username: The username to poll session status for.
            poll_interval: Time in seconds between poll attempts (default: 1.5).

        Returns:
            Session payload dict when status becomes "active".

        Raises:
            InvalidAPIKeyError: If the API key is invalid.
            KNAIError: For other API errors.
        """
        url = f"{self._base_url}/providers/session/status"
        params = {"provider_username": provider_username}
        headers = self._get_headers()

        while True:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            )

            if not response.ok:
                self._handle_error_response(response)

            data = response.json()

            if data.get("status") == "active":
                return data

            time.sleep(poll_interval)

    def charge(
        self,
        session_token: str,
        amount_tokens: int,
        model: str,
    ) -> Dict[str, Any]:
        """
        Charge wallet usage for the current session.

        Args:
            session_token: The active session token authorizing the charge.
            amount_tokens: Number of tokens to charge.
            model: The model identifier being used.

        Returns:
            Parsed JSON response from the charge API.

        Raises:
            SessionExpiredError: If the session has expired.
            InsufficientBalanceError: If wallet balance is insufficient.
            InvalidAPIKeyError: If the API key is invalid.
            KNAIError: For other API errors.
        """
        if not session_token:
            raise ValueError("session_token is required")
        if amount_tokens <= 0:
            raise ValueError("amount_tokens must be positive")
        if not model:
            raise ValueError("model is required")

        url = f"{self._base_url}/charge/authorize"
        headers = self._get_headers(session_token=session_token)
        payload = {
            "amount_tokens": amount_tokens,
            "model": model,
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )

        if not response.ok:
            self._handle_error_response(response)

        return response.json()
