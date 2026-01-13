"""Billing resource for TradePose Client.

This module provides methods for managing subscriptions, plans, and usage.
"""

import logging

from tradepose_models.billing import (
    CheckoutRequest,
    CheckoutResponse,
    PlansListResponse,
    SubscriptionDetailResponse,
    UsageHistoryResponse,
    UsageStatsResponse,
)

from .base import BaseResource

logger = logging.getLogger(__name__)


class BillingResource(BaseResource):
    """Billing and subscription management resource.

    This resource provides methods to manage subscriptions, view plans,
    and track usage statistics.

    Example:
        >>> async with TradePoseClient(api_key="tp_live_xxx") as client:
        ...     # View available plans
        ...     plans = await client.billing.list_plans()
        ...     for plan in plans.plans:
        ...         print(f"{plan.name}: ${plan.price_monthly}/mo")
        ...
        ...     # Get current subscription
        ...     sub = await client.billing.get_subscription()
        ...     print(f"Plan: {sub.current_plan.name}")
        ...     print(f"Usage: {sub.usage_current_month}/{sub.usage_limit}")
        ...
        ...     # Check usage stats
        ...     usage = await client.billing.get_usage()
        ...     print(f"Requests this month: {usage.current_month.usage}")
    """

    async def list_plans(self) -> PlansListResponse:
        """List all available subscription plans.

        Returns all plans with pricing, limits, and features.
        This endpoint does not require authentication.

        Returns:
            PlansListResponse with list of all available plans

        Raises:
            TradePoseAPIError: For API errors

        Example:
            >>> plans = await client.billing.list_plans()
            >>> for plan in plans.plans:
            ...     print(f"{plan.name} ({plan.tier})")
            ...     print(f"  Price: ${plan.price_monthly}/mo or ${plan.price_yearly}/yr")
            ...     print(f"  Limits: {plan.limits.monthly_quota} requests/month")
            ...     print(f"  Features: {', '.join(plan.features)}")
        """
        logger.debug("Listing subscription plans")

        response = await self._get("/api/v1/billing/plans")

        result = PlansListResponse(**response)
        logger.info(f"Listed {len(result.plans)} plans")
        return result

    async def create_checkout(
        self,
        plan_tier: str,
        billing_cycle: str,
    ) -> CheckoutResponse:
        """Create a checkout session for subscription.

        Creates a Lemon Squeezy checkout URL for the specified plan.
        User will be redirected to complete payment.

        Args:
            plan_tier: Plan tier ('free', 'pro', 'enterprise')
            billing_cycle: Billing cycle ('monthly', 'yearly')

        Returns:
            CheckoutResponse with checkout_url and variant_id

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If plan_tier or billing_cycle is invalid
            TradePoseAPIError: For other API errors

        Example:
            >>> checkout = await client.billing.create_checkout(
            ...     plan_tier="pro",
            ...     billing_cycle="yearly"
            ... )
            >>> print(f"Complete checkout at: {checkout.checkout_url}")
        """
        logger.info(f"Creating checkout session: {plan_tier} ({billing_cycle})")

        request = CheckoutRequest(
            plan_tier=plan_tier,
            billing_cycle=billing_cycle,
        )
        response = await self._post(
            "/api/v1/billing/checkout",
            json=request,
        )

        result = CheckoutResponse(**response)
        logger.info(f"Checkout session created: {result.variant_id}")
        return result

    async def get_subscription(self) -> SubscriptionDetailResponse:
        """Get current subscription details.

        Returns detailed subscription information including plan details,
        current usage, and limits.

        Returns:
            SubscriptionDetailResponse with subscription and usage info

        Raises:
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> sub = await client.billing.get_subscription()
            >>> if sub.subscription:
            ...     print(f"Status: {sub.subscription.status}")
            ...     print(f"Period: {sub.subscription.period_start} to {sub.subscription.period_end}")
            ... print(f"Plan: {sub.current_plan.name}")
            ... print(f"Usage: {sub.usage_current_month}/{sub.usage_limit}")
        """
        logger.debug("Getting subscription details")

        response = await self._get("/api/v1/billing/subscription")

        result = SubscriptionDetailResponse(**response)
        logger.info(f"Retrieved subscription: {result.current_plan.tier}")
        return result

    async def cancel_subscription(self) -> dict:
        """Cancel current subscription.

        Cancels the subscription at the end of the current billing period.
        Access continues until period_end date.

        Returns:
            Cancellation confirmation message

        Raises:
            AuthenticationError: If authentication fails
            ResourceNotFoundError: If no active subscription
            TradePoseAPIError: For other API errors

        Example:
            >>> result = await client.billing.cancel_subscription()
            >>> print(result["message"])
        """
        logger.info("Cancelling subscription")

        response = await self._post("/api/v1/billing/cancel")

        logger.info("Subscription cancelled")
        return response  # type: ignore

    async def get_usage(self) -> UsageStatsResponse:
        """Get current usage statistics.

        Returns usage statistics for the current billing period including
        request count, limits, and remaining quota.

        Returns:
            UsageStatsResponse with current usage stats

        Raises:
            AuthenticationError: If authentication fails
            TradePoseAPIError: For other API errors

        Example:
            >>> usage = await client.billing.get_usage()
            >>> print(f"Plan: {usage.plan_name} ({usage.plan_tier})")
            >>> print(f"Usage: {usage.current_month.usage}/{usage.monthly_quota}")
            >>> print(f"Remaining: {usage.current_month.remaining}")
            >>> print(f"Percentage used: {usage.current_month.percentage_used:.1f}%")
        """
        logger.debug("Getting usage statistics")

        response = await self._get("/api/v1/billing/usage")

        result = UsageStatsResponse(**response)
        logger.info(
            f"Usage: {result.current_month.usage}/{result.monthly_quota} "
            f"({result.current_month.percentage_used:.1f}%)"
        )
        return result

    async def get_usage_history(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> UsageHistoryResponse:
        """Get historical usage data.

        Returns daily usage breakdown for the specified date range.
        If dates are not specified, returns current month's usage.

        Args:
            start_date: Start date in ISO 8601 format (YYYY-MM-DD), optional
            end_date: End date in ISO 8601 format (YYYY-MM-DD), optional

        Returns:
            UsageHistoryResponse with daily usage breakdown

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If dates are invalid
            TradePoseAPIError: For other API errors

        Example:
            >>> # Get current month's usage
            >>> history = await client.billing.get_usage_history()
            >>> print(f"Total requests: {history.total_requests}")
            >>> for day in history.daily_usage:
            ...     print(f"{day.usage_date}: {day.request_count} requests")
            >>>
            >>> # Get specific date range
            >>> history = await client.billing.get_usage_history(
            ...     start_date="2024-01-01",
            ...     end_date="2024-01-31"
            ... )
        """
        logger.debug(f"Getting usage history: {start_date} to {end_date}")

        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._get(
            "/api/v1/billing/usage/history",
            params=params,
        )

        result = UsageHistoryResponse(**response)
        logger.info(
            f"Usage history: {result.total_requests} requests "
            f"({result.start_date} to {result.end_date})"
        )
        return result
