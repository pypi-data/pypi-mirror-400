"""Usage resource for TradePose Client."""

import logging

from tradepose_models.billing import DetailedUsageResponse

from .base import BaseResource

logger = logging.getLogger(__name__)


class UsageResource(BaseResource):
    """Usage statistics resource.

    Provides methods to retrieve detailed usage statistics across
    multiple time windows (last minute, hour, day, and current billing period).

    Example:
        ```python
        async with TradePoseClient(api_key="your_api_key") as client:
            # Get detailed usage statistics
            usage = await client.usage.get_current()

            print(f"Plan: {usage.plan}")
            print(f"Quota: {usage.current_period.completed_tasks}/{usage.monthly_quota}")
            print(f"Usage: {usage.quota_percentage_used:.1f}%")
            print(f"Last minute: {usage.last_minute.total_requests} requests")
        ```
    """

    async def get_current(self) -> DetailedUsageResponse:
        """Get current detailed usage statistics.

        Retrieves comprehensive usage statistics including:
        - Last minute usage
        - Last hour usage
        - Last 24 hours usage
        - Current billing period usage
        - Plan limits and quotas
        - Remaining quota

        The data is cached on the server for 3 minutes to improve performance.

        Returns:
            DetailedUsageResponse: Detailed usage statistics with all time windows

        Raises:
            AuthenticationError: If authentication fails (invalid API key or JWT)
            TradePoseAPIError: For other API errors

        Example:
            ```python
            usage = await client.usage.get_current()

            # Access current period stats
            print(f"Completed tasks: {usage.current_period.completed_tasks}")
            print(f"Failed tasks: {usage.current_period.failed_tasks}")
            print(f"Total requests: {usage.current_period.total_requests}")

            # Check quota
            if usage.remaining_quota < 10:
                print("Warning: Running low on quota!")
            ```
        """
        logger.debug("Getting current detailed usage statistics")

        response = await self._get("/api/v1/usage/current")

        result = DetailedUsageResponse(**response)

        logger.info(
            f"Usage statistics retrieved - "
            f"{result.current_period.completed_tasks}/{result.monthly_quota} "
            f"({result.quota_percentage_used:.1f}% used)"
        )

        return result
