"""
RevHold API Client
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    raise ImportError(
        "The requests library is required. Install it with: pip install requests"
    )

from .exceptions import RevHoldError


class RevHold:
    """RevHold API client for tracking usage events and querying AI insights."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.revhold.io/api",
        timeout: int = 30,
    ):
        """
        Initialize the RevHold client.

        Args:
            api_key: Your RevHold API key
            base_url: API base URL (defaults to production)
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"revhold-python/{self.__class__.__module__}",
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the RevHold API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: URL query parameters

        Returns:
            Response data as dictionary

        Raises:
            RevHoldError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )

            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"message": response.text}

            # Check for errors
            if not response.ok:
                raise RevHoldError(
                    message=response_data.get("message", "An error occurred"),
                    status_code=response.status_code,
                    error_code=response_data.get("error", "unknown_error"),
                    details=response_data,
                )

            return response_data

        except requests.exceptions.RequestException as e:
            raise RevHoldError(
                message=str(e),
                status_code=0,
                error_code="network_error",
            ) from e

    def track_event(
        self,
        user_id: str,
        event_name: str,
        event_value: Union[int, float] = 1,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track a single usage event.

        Args:
            user_id: Unique identifier for the user
            event_name: Name of the event (e.g., 'feature_used')
            event_value: Numeric value (defaults to 1)
            timestamp: ISO 8601 timestamp (defaults to current time)

        Returns:
            Response containing success status, message, and event ID

        Example:
            >>> revhold.track_event(
            ...     user_id='user_123',
            ...     event_name='document_created',
            ...     event_value=1
            ... )
            {'success': True, 'message': 'Usage event recorded', 'eventId': 'evt_xyz'}
        """
        payload = {
            "userId": user_id,
            "eventName": event_name,
            "eventValue": event_value,
            "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
        }

        return self._request("POST", "/usage", data=payload)

    def track_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Track multiple events in parallel.

        Args:
            events: List of event dictionaries with user_id, event_name, etc.

        Returns:
            Response containing success status and count

        Example:
            >>> revhold.track_batch([
            ...     {'user_id': 'user_1', 'event_name': 'feature_used'},
            ...     {'user_id': 'user_2', 'event_name': 'document_created'},
            ... ])
            {'success': True, 'message': 'Batch events tracked', 'count': 2}
        """
        results = []
        errors = []

        for event in events:
            try:
                result = self.track_event(
                    user_id=event.get("user_id", ""),
                    event_name=event.get("event_name", ""),
                    event_value=event.get("event_value", 1),
                    timestamp=event.get("timestamp"),
                )
                results.append(result)
            except RevHoldError as e:
                errors.append({"event": event, "error": str(e)})

        if errors and not results:
            # All failed
            raise RevHoldError(
                message=f"All {len(errors)} events failed",
                status_code=400,
                error_code="batch_failed",
                details={"errors": errors},
            )

        return {
            "success": True,
            "message": "Batch events tracked successfully",
            "count": len(results),
            "errors": errors if errors else None,
        }

    def ask_ai(self, question: str) -> Dict[str, Any]:
        """
        Ask the AI a question about your usage data.

        Args:
            question: Your question in plain English

        Returns:
            AI response with answer, confidence level, and data points analyzed

        Example:
            >>> result = revhold.ask_ai('Which users are most engaged this week?')
            >>> print(result['answer'])
            'Based on your usage data, 5 users are highly engaged...'
        """
        payload = {"question": question}
        return self._request("POST", "/ai", data=payload)

    def get_usage(
        self, limit: Optional[int] = None, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve recent usage events.

        Args:
            limit: Maximum number of events to return (default: 100, max: 1000)
            user_id: Filter events by specific user ID

        Returns:
            Response containing events array, total count, and limit

        Example:
            >>> usage = revhold.get_usage(limit=10)
            >>> print(f"Found {usage['total']} events")
            >>> for event in usage['events']:
            ...     print(event['eventName'])
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if user_id is not None:
            params["userId"] = user_id

        return self._request("GET", "/usage", params=params)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self._session.close()

    def close(self):
        """Close the underlying HTTP session."""
        self._session.close()

