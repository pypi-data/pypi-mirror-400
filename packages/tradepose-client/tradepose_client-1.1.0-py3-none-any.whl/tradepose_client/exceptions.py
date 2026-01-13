"""Custom exceptions for TradePose Client.

This module defines a comprehensive exception hierarchy for handling
various error scenarios when interacting with the TradePose Gateway API.
"""

from typing import Any


class TradePoseError(Exception):
    """Base exception for all TradePose client errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize TradePoseError.

        Args:
            message: Error message
            **kwargs: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.context = kwargs


class TradePoseConfigError(TradePoseError):
    """Configuration error (invalid settings, missing credentials, etc.)."""


class TradePoseAPIError(TradePoseError):
    """Base exception for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize TradePoseAPIError.

        Args:
            message: Error message
            status_code: HTTP status code
            response: API response body
            request_id: Request ID for debugging
            **kwargs: Additional error context
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response = response
        self.request_id = request_id


class AuthenticationError(TradePoseAPIError):
    """Authentication failed (invalid API key, expired JWT, etc.)."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key or JWT token.",
        **kwargs: Any,
    ) -> None:
        """Initialize AuthenticationError."""
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(TradePoseAPIError):
    """Authorization failed (insufficient permissions, subscription required, etc.)."""

    def __init__(
        self,
        message: str = "Authorization failed. You do not have permission to access this resource.",
        **kwargs: Any,
    ) -> None:
        """Initialize AuthorizationError."""
        super().__init__(message, status_code=403, **kwargs)


class ResourceNotFoundError(TradePoseAPIError):
    """Resource not found (task, strategy, etc.)."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize ResourceNotFoundError.

        Args:
            resource_type: Type of resource (e.g., 'task', 'strategy')
            resource_id: Resource identifier
            **kwargs: Additional error context
        """
        message = f"{resource_type.capitalize()} '{resource_id}' not found."
        super().__init__(message, status_code=404, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ValidationError(TradePoseAPIError):
    """Request validation failed (invalid parameters, missing fields, etc.)."""

    def __init__(
        self,
        message: str,
        errors: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ValidationError.

        Args:
            message: Error message
            errors: List of validation errors
            **kwargs: Additional error context
        """
        super().__init__(message, status_code=422, **kwargs)
        self.errors = errors or []


class RateLimitError(TradePoseAPIError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize RateLimitError.

        Args:
            message: Error message
            retry_after: Seconds until rate limit resets
            **kwargs: Additional error context
        """
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class ServerError(TradePoseAPIError):
    """Server error (5xx status codes)."""

    def __init__(
        self,
        message: str = "Server error. Please try again later.",
        **kwargs: Any,
    ) -> None:
        """Initialize ServerError."""
        super().__init__(message, **kwargs)


class NetworkError(TradePoseError):
    """Network error (connection timeout, DNS failure, etc.)."""

    def __init__(
        self,
        message: str = "Network error. Please check your connection.",
        **kwargs: Any,
    ) -> None:
        """Initialize NetworkError."""
        super().__init__(message, **kwargs)


class TaskError(TradePoseError):
    """Base exception for task-related errors."""

    def __init__(
        self,
        message: str,
        task_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize TaskError.

        Args:
            message: Error message
            task_id: Task identifier
            **kwargs: Additional error context
        """
        super().__init__(message, **kwargs)
        self.task_id = task_id


class TaskTimeoutError(TaskError):
    """Task polling timed out."""

    def __init__(
        self,
        task_id: str,
        timeout: float,
        **kwargs: Any,
    ) -> None:
        """Initialize TaskTimeoutError.

        Args:
            task_id: Task identifier
            timeout: Timeout duration in seconds
            **kwargs: Additional error context
        """
        message = f"Task '{task_id}' timed out after {timeout} seconds."
        super().__init__(message, task_id=task_id, **kwargs)
        self.timeout = timeout


class TaskFailedError(TaskError):
    """Task execution failed."""

    def __init__(
        self,
        task_id: str,
        error: str,
        **kwargs: Any,
    ) -> None:
        """Initialize TaskFailedError.

        Args:
            task_id: Task identifier
            error: Error message from task execution
            **kwargs: Additional error context
        """
        message = f"Task '{task_id}' failed: {error}"
        super().__init__(message, task_id=task_id, **kwargs)
        self.error = error


class TaskCancelledError(TaskError):
    """Task was cancelled."""

    def __init__(
        self,
        task_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize TaskCancelledError.

        Args:
            task_id: Task identifier
            **kwargs: Additional error context
        """
        message = f"Task '{task_id}' was cancelled."
        super().__init__(message, task_id=task_id, **kwargs)


class SerializationError(TradePoseError):
    """Data serialization/deserialization error."""

    def __init__(
        self,
        message: str,
        data_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SerializationError.

        Args:
            message: Error message
            data_type: Type of data being serialized (e.g., 'parquet', 'json')
            **kwargs: Additional error context
        """
        super().__init__(message, **kwargs)
        self.data_type = data_type


class SchemaValidationError(SerializationError):
    """Data schema validation failed."""

    def __init__(
        self,
        message: str,
        expected_schema: str | None = None,
        actual_columns: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SchemaValidationError.

        Args:
            message: Error message
            expected_schema: Name of expected schema
            actual_columns: Actual columns in data
            **kwargs: Additional error context
        """
        super().__init__(message, **kwargs)
        self.expected_schema = expected_schema
        self.actual_columns = actual_columns


class SubscriptionError(TradePoseError):
    """Subscription-related error (plan limit exceeded, no active subscription, etc.)."""

    def __init__(
        self,
        message: str,
        subscription_status: str | None = None,
        limits_exceeded: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SubscriptionError.

        Args:
            message: Error message
            subscription_status: Current subscription status
            limits_exceeded: List of limits that were exceeded
            **kwargs: Additional error context
        """
        super().__init__(message, **kwargs)
        self.subscription_status = subscription_status
        self.limits_exceeded = limits_exceeded or []


class StrategyError(TradePoseError):
    """Strategy-related error (invalid strategy code, compilation error, etc.)."""

    def __init__(
        self,
        message: str,
        strategy_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize StrategyError.

        Args:
            message: Error message
            strategy_name: Name of strategy
            **kwargs: Additional error context
        """
        super().__init__(message, **kwargs)
        self.strategy_name = strategy_name
