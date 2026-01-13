"""Portfolio CRUD resource for TradePose Client.

This module provides operations for managing portfolios.
"""

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from .base import BaseResource

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class BlueprintSelection(BaseModel):
    """Blueprint selection for portfolio."""

    strategy_name: str = Field(..., description="Strategy name")
    blueprint_name: str = Field(..., description="Blueprint name")


class PortfolioCreateRequest(BaseModel):
    """Portfolio creation request."""

    name: str = Field(..., description="Portfolio name")
    capital: Decimal = Field(..., description="Portfolio capital")
    currency: str = Field(..., description="Currency code (e.g., USD)")
    platform: str = Field(..., description="Trading platform (e.g., MT5)")
    selections: list[BlueprintSelection] = Field(
        default_factory=list, description="Blueprint selections"
    )
    instrument_mapping: dict | None = Field(None, description="Instrument mapping (base -> target)")


class PortfolioUpdateRequest(BaseModel):
    """Portfolio update request."""

    capital: Decimal | None = Field(None, description="New capital")
    selections: list[BlueprintSelection] | None = Field(
        None, description="New selections (replaces all)"
    )
    instrument_mapping: dict | None = Field(None, description="New instrument mapping")


class PortfolioResponse(BaseModel):
    """Portfolio response model."""

    name: str
    capital: Decimal
    currency: str
    platform: str
    selections: list[BlueprintSelection]
    instrument_mapping: dict | None = None


class PortfolioListResponse(BaseModel):
    """Portfolio list response."""

    portfolios: list[PortfolioResponse]
    count: int


# =============================================================================
# RESOURCE CLASS
# =============================================================================


class PortfoliosResource(BaseResource):
    """Portfolio management resource.

    Provides operations for creating, reading, updating, and deleting portfolios.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Create a portfolio
        ...     portfolio = await client.portfolios.create(
        ...         PortfolioCreateRequest(
        ...             name="Gold_Portfolio",
        ...             capital=Decimal("100000"),
        ...             currency="USD",
        ...             platform="MT5",
        ...             selections=[
        ...                 BlueprintSelection(
        ...                     strategy_name="SuperTrend",
        ...                     blueprint_name="trend_follow"
        ...                 )
        ...             ]
        ...         )
        ...     )
        ...
        ...     # List all portfolios
        ...     portfolios = await client.portfolios.list()
    """

    async def create(self, request: PortfolioCreateRequest) -> PortfolioResponse:
        """Create a new portfolio.

        Args:
            request: Portfolio creation request

        Returns:
            Created portfolio

        Raises:
            ValidationError: If request data is invalid
            TradePoseAPIError: For other API errors
        """
        logger.info(f"Creating portfolio: {request.name}")

        response = await self._post("/api/v1/portfolios", json=request)

        result = PortfolioResponse(**response)
        logger.info(f"Created portfolio: {result.name}")
        return result

    async def list(self, *, archived: bool = False) -> PortfolioListResponse:
        """List all portfolios.

        Args:
            archived: Include archived portfolios

        Returns:
            List of portfolios

        Raises:
            TradePoseAPIError: For API errors
        """
        logger.debug(f"Listing portfolios (archived={archived})")

        params = {"archived": archived} if archived else None
        response = await self._get("/api/v1/portfolios", params=params)

        result = PortfolioListResponse(**response)
        logger.info(f"Listed {result.count} portfolios")
        return result

    async def get(self, name: str) -> PortfolioResponse:
        """Get portfolio by name.

        Args:
            name: Portfolio name

        Returns:
            Portfolio with selections

        Raises:
            ResourceNotFoundError: If portfolio not found
            TradePoseAPIError: For other API errors
        """
        logger.debug(f"Getting portfolio: {name}")

        response = await self._get(f"/api/v1/portfolios/{name}")

        result = PortfolioResponse(**response)
        logger.info(f"Retrieved portfolio: {result.name}")
        return result

    async def update(
        self,
        name: str,
        request: PortfolioUpdateRequest,
    ) -> PortfolioResponse:
        """Update a portfolio.

        Args:
            name: Portfolio name
            request: Update request

        Returns:
            Updated portfolio

        Raises:
            ResourceNotFoundError: If portfolio not found
            ValidationError: If update data is invalid
            TradePoseAPIError: For other API errors
        """
        logger.info(f"Updating portfolio: {name}")

        response = await self._put(f"/api/v1/portfolios/{name}", json=request)

        result = PortfolioResponse(**response)
        logger.info(f"Updated portfolio: {result.name}")
        return result

    async def delete(self, name: str, *, archive: bool = True) -> dict:
        """Delete or archive a portfolio.

        Args:
            name: Portfolio name
            archive: If True, soft delete (archive). If False, hard delete.

        Returns:
            Success message

        Raises:
            ResourceNotFoundError: If portfolio not found
            ValidationError: If portfolio has bindings (for hard delete)
            TradePoseAPIError: For other API errors
        """
        action = "Archiving" if archive else "Deleting"
        logger.info(f"{action} portfolio: {name}")

        params = {"archive": archive}
        response = await self._delete(f"/api/v1/portfolios/{name}", params=params)

        logger.info(f"Portfolio {name} {'archived' if archive else 'deleted'}")
        return response  # type: ignore
