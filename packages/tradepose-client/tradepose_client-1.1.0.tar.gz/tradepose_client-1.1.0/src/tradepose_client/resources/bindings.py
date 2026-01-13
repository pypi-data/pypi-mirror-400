"""Account-Portfolio Binding resource for TradePose Client.

This module provides operations for managing account-portfolio bindings.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseResource

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class BindingCreateRequest(BaseModel):
    """Binding creation request."""

    account_id: UUID = Field(..., description="Account UUID")
    portfolio_name: str = Field(..., description="Portfolio name")
    execution_mode: str = Field(
        default="signal_priority",
        description="Execution mode: price_priority or signal_priority",
    )


class BindingResponse(BaseModel):
    """Binding response model."""

    id: UUID
    user_id: UUID
    account_id: UUID
    portfolio_id: UUID
    execution_mode: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BindingListResponse(BaseModel):
    """Binding list response."""

    bindings: list[BindingResponse]
    count: int


# =============================================================================
# RESOURCE CLASS
# =============================================================================


class BindingsResource(BaseResource):
    """Account-Portfolio binding management resource.

    Provides operations for creating, listing, and deleting bindings
    between accounts and portfolios.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Create a binding
        ...     binding = await client.bindings.create(
        ...         BindingCreateRequest(
        ...             account_id=UUID("..."),
        ...             portfolio_name="Gold_Portfolio",
        ...             execution_mode="signal_priority"
        ...         )
        ...     )
        ...
        ...     # List all bindings
        ...     bindings = await client.bindings.list()
        ...
        ...     # Delete a binding
        ...     await client.bindings.delete(binding.id)
    """

    async def create(self, request: BindingCreateRequest) -> BindingResponse:
        """Create account-portfolio binding.

        Validates that portfolio platform matches account broker_type.

        Args:
            request: Binding creation request

        Returns:
            Created binding

        Raises:
            ValidationError: Platform mismatch or validation error
            ResourceNotFoundError: Account or portfolio not found
            TradePoseAPIError: For other API errors
        """
        logger.info(
            f"Creating binding: account={request.account_id}, portfolio={request.portfolio_name}"
        )

        response = await self._post("/api/v1/bindings", json=request)

        result = BindingResponse(**response)
        logger.info(f"Created binding: {result.id}")
        return result

    async def list(self) -> BindingListResponse:
        """List all bindings for the user.

        Returns:
            List of bindings

        Raises:
            TradePoseAPIError: For API errors
        """
        logger.debug("Listing bindings")

        response = await self._get("/api/v1/bindings")

        result = BindingListResponse(**response)
        logger.info(f"Listed {result.count} bindings")
        return result

    async def delete(self, binding_id: UUID) -> dict:
        """Delete a binding.

        Args:
            binding_id: Binding UUID

        Returns:
            Success message

        Raises:
            ResourceNotFoundError: If binding not found
            TradePoseAPIError: For other API errors
        """
        logger.info(f"Deleting binding: {binding_id}")

        response = await self._delete(f"/api/v1/bindings/{binding_id}")

        logger.info(f"Deleted binding: {binding_id}")
        return response  # type: ignore
