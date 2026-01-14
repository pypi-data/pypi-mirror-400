from typing import Any, Optional
from urllib.parse import urljoin

import httpx

from .errors import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    FourbyfourError,
    InternalError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class HttpClient:
    """HTTP client for making API requests."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def _build_url(self, path: str) -> str:
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _handle_error(self, response: httpx.Response) -> None:
        try:
            data = response.json()
            message = data.get("error", {}).get("message", response.reason_phrase)
        except Exception:
            message = response.reason_phrase or "Unknown error"

        status = response.status_code

        if status == 400:
            raise ValidationError(message)
        elif status == 401:
            raise AuthenticationError(message)
        elif status == 403:
            raise ForbiddenError(message)
        elif status == 404:
            raise NotFoundError(message)
        elif status == 409:
            raise ConflictError(message)
        elif status == 429:
            raise RateLimitError(message)
        elif status >= 500:
            raise InternalError(message)
        else:
            raise FourbyfourError(message, "UNKNOWN_ERROR", status)

    def get(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> Any:
        url = self._build_url(path)
        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        response = self._client.get(url, params=params)
        if not response.is_success:
            self._handle_error(response)
        if response.status_code == 204:
            return None
        return response.json()

    def post(self, path: str, data: Optional[dict[str, Any]] = None) -> Any:
        url = self._build_url(path)
        response = self._client.post(url, json=data)
        if not response.is_success:
            self._handle_error(response)
        if response.status_code == 204:
            return None
        return response.json()

    def delete(self, path: str) -> None:
        url = self._build_url(path)
        response = self._client.delete(url)
        if not response.is_success:
            self._handle_error(response)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
