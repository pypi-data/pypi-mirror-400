"""Error types for the Target SDK."""

from typing import Optional


# Error codes returned by the Target API
ERR_UNAUTHORIZED = "UNAUTHORIZED"
ERR_INVALID_REQUEST = "INVALID_REQUEST"
ERR_NOT_FOUND = "NOT_FOUND"
ERR_UPSTREAM_ERROR = "UPSTREAM_ERROR"
ERR_INTERNAL_ERROR = "INTERNAL_ERROR"
ERR_INVENTORY_UNAVAILABLE = "INVENTORY_UNAVAILABLE"


class TargetError(Exception):
    """Base exception for Target SDK errors."""

    pass


class APIError(TargetError):
    """Exception raised when the Target API returns an error response."""

    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
        code: Optional[str] = None,
        http_status: Optional[int] = None,
    ):
        self.message = message
        self.status = status
        self.details = details
        self.suggestion = suggestion
        self.code = code
        self.http_status = http_status
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.details:
            return f"target: {self.message} ({self.details})"
        if self.code:
            return f"target: [{self.code}] {self.message}"
        return f"target: {self.message}"

    def is_unauthorized(self) -> bool:
        """Check if this is an authentication error."""
        return self.http_status == 401

    def is_not_found(self) -> bool:
        """Check if the requested resource was not found."""
        return self.http_status == 404

    def is_invalid_request(self) -> bool:
        """Check if this error is due to an invalid request."""
        return self.http_status == 400

    def is_upstream_error(self) -> bool:
        """Check if this error is from an upstream service."""
        return self.http_status == 502

    def is_internal_error(self) -> bool:
        """Check if this is an internal server error."""
        return self.http_status == 500

    def is_inventory_unavailable(self) -> bool:
        """Check if the item is not available for the selected fulfillment method."""
        return self.code == ERR_INVENTORY_UNAVAILABLE or self.http_status == 424


class RequestError(TargetError):
    """Exception raised when a request fails (network error, timeout, etc.)."""

    pass
