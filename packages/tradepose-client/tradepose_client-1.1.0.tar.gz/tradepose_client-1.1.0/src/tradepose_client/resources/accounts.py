"""Account CRUD resource for TradePose Client.

This module provides operations for managing broker accounts.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from tradepose_models.broker import AccountStatus, BrokerType, MarketType

from .base import BaseResource

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class AccountCreateRequest(BaseModel):
    """Account creation request."""

    name: str = Field(..., description="Account name (unique per user)")
    broker_type: BrokerType = Field(..., description="Broker type")
    credentials: dict = Field(
        ..., description="Raw credentials (api_key, api_secret, passphrase, etc.)"
    )
    available_markets: list[MarketType] = Field(
        default=[MarketType.SPOT], description="Available market types"
    )
    default_market: MarketType | None = Field(None, description="Default market type")
    environment: str = Field(default="production", description="Environment")
    base_url: str | None = Field(None, description="API base URL override")
    ws_url: str | None = Field(None, description="WebSocket URL override")
    status: AccountStatus = Field(default=AccountStatus.INACTIVE, description="Initial status")


class AccountUpdateRequest(BaseModel):
    """Account update request."""

    name: str | None = Field(None, description="New account name")
    credentials: dict | None = Field(None, description="New credentials (will be encrypted)")
    available_markets: list[MarketType] | None = Field(None, description="New market types")
    default_market: MarketType | None = Field(None, description="New default market")
    environment: str | None = Field(None, description="New environment")
    base_url: str | None = Field(None, description="New base URL")
    ws_url: str | None = Field(None, description="New WebSocket URL")
    status: AccountStatus | None = Field(None, description="New status")


class AccountResponse(BaseModel):
    """Account response model."""

    id: str
    name: str
    broker_type: BrokerType
    available_markets: list[MarketType]
    default_market: MarketType | None = None
    environment: str
    base_url: str | None = None
    ws_url: str | None = None
    status: AccountStatus
    is_archived: bool
    last_validated_at: datetime | None = None
    validation_error: str | None = None
    created_at: datetime
    updated_at: datetime


class AccountListResponse(BaseModel):
    """Account list response."""

    accounts: list[AccountResponse]
    count: int


# =============================================================================
# RESOURCE CLASS
# =============================================================================


class AccountsResource(BaseResource):
    """Account management resource.

    Provides operations for creating, reading, updating, and deleting broker accounts.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # Create an account
        ...     account = await client.accounts.create(
        ...         AccountCreateRequest(
        ...             name="My Binance Account",
        ...             broker_type=BrokerType.BINANCE,
        ...             credentials={
        ...                 "api_key": "xxx",
        ...                 "api_secret": "yyy"
        ...             },
        ...             available_markets=[MarketType.SPOT, MarketType.FUTURES],
        ...             status=AccountStatus.ACTIVE
        ...         )
        ...     )
        ...
        ...     # List all accounts
        ...     accounts = await client.accounts.list()
    """

    async def create(self, request: AccountCreateRequest) -> AccountResponse:
        """Create a new broker account.

        Args:
            request: Account creation request

        Returns:
            Created account

        Raises:
            ValidationError: If request data is invalid
            TradePoseAPIError: For other API errors
        """
        logger.info(f"Creating account: {request.name}")

        response = await self._post("/api/v1/accounts", json=request)

        result = AccountResponse(**response)
        logger.info(f"Created account: {result.id}")
        return result

    async def list(self, *, archived: bool = False) -> AccountListResponse:
        """List all accounts.

        Args:
            archived: Include archived accounts

        Returns:
            List of accounts

        Raises:
            TradePoseAPIError: For API errors
        """
        logger.debug(f"Listing accounts (archived={archived})")

        params = {"archived": archived} if archived else None
        response = await self._get("/api/v1/accounts", params=params)

        result = AccountListResponse(**response)
        logger.info(f"Listed {result.count} accounts")
        return result

    async def get(self, account_id: str) -> AccountResponse:
        """Get account by ID.

        Args:
            account_id: Account UUID

        Returns:
            Account details

        Raises:
            ResourceNotFoundError: If account not found
            TradePoseAPIError: For other API errors
        """
        logger.debug(f"Getting account: {account_id}")

        response = await self._get(f"/api/v1/accounts/{account_id}")

        result = AccountResponse(**response)
        logger.info(f"Retrieved account: {result.id}")
        return result

    async def update(
        self,
        account_id: str,
        request: AccountUpdateRequest,
    ) -> AccountResponse:
        """Update an account.

        Args:
            account_id: Account UUID
            request: Update request

        Returns:
            Updated account

        Raises:
            ResourceNotFoundError: If account not found
            ValidationError: If update data is invalid
            TradePoseAPIError: For other API errors
        """
        logger.info(f"Updating account: {account_id}")

        response = await self._put(f"/api/v1/accounts/{account_id}", json=request)

        result = AccountResponse(**response)
        logger.info(f"Updated account: {result.id}")
        return result

    async def delete(self, account_id: str, *, archive: bool = True) -> dict:
        """Delete or archive an account.

        Args:
            account_id: Account UUID
            archive: If True, soft delete (archive). If False, hard delete.

        Returns:
            Success message

        Raises:
            ResourceNotFoundError: If account not found
            ValidationError: If account has bindings (for hard delete)
            TradePoseAPIError: For other API errors
        """
        action = "Archiving" if archive else "Deleting"
        logger.info(f"{action} account: {account_id}")

        params = {"archive": archive}
        response = await self._delete(f"/api/v1/accounts/{account_id}", params=params)

        logger.info(f"Account {account_id} {'archived' if archive else 'deleted'}")
        return response  # type: ignore
