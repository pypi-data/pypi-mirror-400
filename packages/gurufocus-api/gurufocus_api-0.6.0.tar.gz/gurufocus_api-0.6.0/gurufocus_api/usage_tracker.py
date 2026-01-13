"""Smart API usage tracking with local decrement and periodic sync.

This module provides a tracker that estimates remaining API calls without
making unnecessary API requests to check quota.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .logging import get_logger

if TYPE_CHECKING:
    from .cache.manager import CacheManager

logger = get_logger(__name__)


@dataclass
class UsageTrackerConfig:
    """Configuration for API usage tracking.

    Attributes:
        enabled: Whether usage tracking is enabled.
        sync_interval_seconds: Seconds between automatic API syncs.
        warn_threshold_percent: Warn when remaining quota below this percentage.
        daily_limit: Expected daily API call limit (for warning calculation).
    """

    enabled: bool = True
    sync_interval_seconds: int = 300  # 5 minutes
    warn_threshold_percent: float = 10.0  # Warn at 10% remaining
    daily_limit: int = 10000  # Default to Premium tier


class APIUsageTracker:
    """Smart API usage tracker with local decrement and periodic sync.

    This tracker maintains a local estimate of remaining API calls by:
    1. Starting with the last known value from cache (if available)
    2. Decrementing locally after each successful API call
    3. Syncing with the actual API periodically or on-demand

    This approach minimizes API calls to check quota while still providing
    reasonable accuracy for quota monitoring.

    Example:
        ```python
        config = UsageTrackerConfig(enabled=True, sync_interval_seconds=300)
        tracker = APIUsageTracker(config)

        # Initialize from cache
        await tracker.initialize(cache)

        # After each API call
        await tracker.decrement()

        # Get estimate without API call
        remaining = await tracker.get_remaining()

        # Sync after calling get_api_usage()
        await tracker.sync(api_remaining=3500)
        ```
    """

    def __init__(self, config: UsageTrackerConfig) -> None:
        """Initialize the usage tracker.

        Args:
            config: Tracker configuration.
        """
        self._config = config
        self._remaining: int | None = None
        self._local_consumed: int = 0
        self._last_sync: float = 0.0
        self._lock = asyncio.Lock()
        self._cache: CacheManager | None = None

    async def initialize(self, cache: CacheManager) -> None:
        """Initialize tracker from cache without making an API call.

        Args:
            cache: The cache manager to load/store values.
        """
        self._cache = cache

        if not self._config.enabled:
            logger.debug("usage_tracker_disabled")
            return

        try:
            # Import here to avoid circular imports
            from .cache.config import CacheCategory

            cached = await cache.get(CacheCategory.API_USAGE, "tracker_state")
            if cached is not None:
                self._remaining = cached.get("remaining")
                self._last_sync = cached.get("synced_at", 0.0)
                logger.debug(
                    "usage_tracker_initialized_from_cache",
                    remaining=self._remaining,
                    last_sync=self._last_sync,
                )
            else:
                logger.debug("usage_tracker_no_cached_state")
        except Exception as e:
            logger.warning("usage_tracker_init_error", error=str(e))

    async def decrement(self) -> None:
        """Decrement local counter after successful API call.

        This should be called after each successful API request.
        Thread-safe via asyncio.Lock.
        """
        if not self._config.enabled:
            return

        async with self._lock:
            self._local_consumed += 1
            logger.debug(
                "usage_tracker_decrement",
                local_consumed=self._local_consumed,
            )

    async def get_remaining(self) -> int | None:
        """Get estimated remaining API calls.

        Returns:
            Estimated remaining calls, or None if never synced.
        """
        if not self._config.enabled or self._remaining is None:
            return None

        async with self._lock:
            estimate = max(0, self._remaining - self._local_consumed)
            return estimate

    def should_sync(self) -> bool:
        """Check if sync interval has elapsed.

        Returns:
            True if it's time to sync with the API.
        """
        if not self._config.enabled:
            return False

        return time.time() - self._last_sync >= self._config.sync_interval_seconds

    async def sync(self, api_remaining: int) -> None:
        """Update tracker after receiving actual API usage data.

        This should be called after a successful get_api_usage() call
        to sync the tracker with actual API quota data.

        Args:
            api_remaining: Actual remaining API calls from the API.
        """
        if not self._config.enabled:
            return

        async with self._lock:
            previous_estimate = (
                max(0, self._remaining - self._local_consumed)
                if self._remaining is not None
                else None
            )

            self._remaining = api_remaining
            self._local_consumed = 0
            self._last_sync = time.time()

            logger.info(
                "usage_tracker_synced",
                api_remaining=api_remaining,
                previous_estimate=previous_estimate,
                drift=abs(api_remaining - previous_estimate)
                if previous_estimate is not None
                else None,
            )

            # Persist to cache for restart recovery
            if self._cache is not None:
                try:
                    from .cache.config import CacheCategory

                    await self._cache.set(
                        CacheCategory.API_USAGE,
                        "tracker_state",
                        value={
                            "remaining": api_remaining,
                            "synced_at": self._last_sync,
                        },
                    )
                except Exception as e:
                    logger.warning("usage_tracker_cache_save_error", error=str(e))

    async def check_warning_threshold(self) -> bool:
        """Check if remaining quota is below warning threshold.

        Returns:
            True if below threshold and warning should be logged.
        """
        if not self._config.enabled:
            return False

        remaining = await self.get_remaining()
        if remaining is None:
            return False

        threshold_calls = self._config.daily_limit * self._config.warn_threshold_percent / 100
        return remaining < threshold_calls

    async def get_stats(self) -> dict[str, Any]:
        """Get tracker statistics.

        Returns:
            Dictionary with tracker state information.
        """
        async with self._lock:
            return {
                "enabled": self._config.enabled,
                "remaining_estimate": max(0, self._remaining - self._local_consumed)
                if self._remaining is not None
                else None,
                "base_remaining": self._remaining,
                "local_consumed": self._local_consumed,
                "last_sync": self._last_sync if self._last_sync > 0 else None,
                "sync_interval_seconds": self._config.sync_interval_seconds,
                "warn_threshold_percent": self._config.warn_threshold_percent,
                "daily_limit": self._config.daily_limit,
            }


class NullUsageTracker(APIUsageTracker):
    """No-op usage tracker when tracking is disabled.

    This provides the same interface as APIUsageTracker but does nothing,
    avoiding conditional checks throughout the codebase.
    """

    def __init__(self) -> None:
        """Initialize the null tracker."""
        super().__init__(UsageTrackerConfig(enabled=False))

    async def initialize(self, cache: CacheManager) -> None:
        """No-op initialize."""
        pass

    async def decrement(self) -> None:
        """No-op decrement."""
        pass

    async def get_remaining(self) -> int | None:
        """Always returns None."""
        return None

    def should_sync(self) -> bool:
        """Always returns False."""
        return False

    async def sync(self, api_remaining: int) -> None:
        """No-op sync."""
        pass

    async def check_warning_threshold(self) -> bool:
        """Always returns False."""
        return False

    async def get_stats(self) -> dict[str, Any]:
        """Return disabled status."""
        return {"enabled": False, "remaining_estimate": None}
