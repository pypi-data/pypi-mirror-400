"""Tests for API usage tracker."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from gurufocus_api.usage_tracker import (
    APIUsageTracker,
    NullUsageTracker,
    UsageTrackerConfig,
)


class TestUsageTrackerConfig:
    """Tests for UsageTrackerConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = UsageTrackerConfig()

        assert config.enabled is True
        assert config.sync_interval_seconds == 300
        assert config.warn_threshold_percent == 10.0
        assert config.daily_limit == 10000

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = UsageTrackerConfig(
            enabled=False,
            sync_interval_seconds=600,
            warn_threshold_percent=5.0,
            daily_limit=100,
        )

        assert config.enabled is False
        assert config.sync_interval_seconds == 600
        assert config.warn_threshold_percent == 5.0
        assert config.daily_limit == 100


class TestAPIUsageTracker:
    """Tests for APIUsageTracker."""

    @pytest.fixture
    def config(self) -> UsageTrackerConfig:
        """Create a test configuration."""
        return UsageTrackerConfig(
            enabled=True,
            sync_interval_seconds=300,
            warn_threshold_percent=10.0,
            daily_limit=10000,
        )

    @pytest.fixture
    def tracker(self, config: UsageTrackerConfig) -> APIUsageTracker:
        """Create a test tracker."""
        return APIUsageTracker(config)

    @pytest.fixture
    def mock_cache(self) -> MagicMock:
        """Create a mock cache manager."""
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        return cache

    @pytest.mark.asyncio
    async def test_initialize_no_cached_state(
        self, tracker: APIUsageTracker, mock_cache: MagicMock
    ) -> None:
        """Test initialization with no cached state."""
        await tracker.initialize(mock_cache)

        assert tracker._remaining is None
        assert tracker._local_consumed == 0

    @pytest.mark.asyncio
    async def test_initialize_with_cached_state(
        self, tracker: APIUsageTracker, mock_cache: MagicMock
    ) -> None:
        """Test initialization with cached state."""
        mock_cache.get = AsyncMock(return_value={"remaining": 5000, "synced_at": time.time() - 60})

        await tracker.initialize(mock_cache)

        assert tracker._remaining == 5000
        assert tracker._local_consumed == 0

    @pytest.mark.asyncio
    async def test_decrement(self, tracker: APIUsageTracker) -> None:
        """Test local decrement."""
        assert tracker._local_consumed == 0

        await tracker.decrement()
        assert tracker._local_consumed == 1

        await tracker.decrement()
        assert tracker._local_consumed == 2

    @pytest.mark.asyncio
    async def test_get_remaining_no_sync(self, tracker: APIUsageTracker) -> None:
        """Test get_remaining when never synced."""
        result = await tracker.get_remaining()

        assert result is None

    @pytest.mark.asyncio
    async def test_get_remaining_after_sync(self, tracker: APIUsageTracker) -> None:
        """Test get_remaining after sync."""
        tracker._remaining = 1000
        tracker._local_consumed = 0

        result = await tracker.get_remaining()

        assert result == 1000

    @pytest.mark.asyncio
    async def test_get_remaining_with_decrement(self, tracker: APIUsageTracker) -> None:
        """Test get_remaining accounts for local decrements."""
        tracker._remaining = 1000

        await tracker.decrement()
        await tracker.decrement()
        await tracker.decrement()

        result = await tracker.get_remaining()

        assert result == 997

    @pytest.mark.asyncio
    async def test_get_remaining_never_negative(self, tracker: APIUsageTracker) -> None:
        """Test get_remaining never returns negative."""
        tracker._remaining = 2
        tracker._local_consumed = 10

        result = await tracker.get_remaining()

        assert result == 0

    def test_should_sync_initial(self, tracker: APIUsageTracker) -> None:
        """Test should_sync returns True initially."""
        # last_sync is 0, so it should always trigger
        result = tracker.should_sync()

        assert result is True

    def test_should_sync_after_interval(self, tracker: APIUsageTracker) -> None:
        """Test should_sync after interval elapsed."""
        tracker._last_sync = time.time() - 400  # 400s ago, interval is 300s

        result = tracker.should_sync()

        assert result is True

    def test_should_sync_before_interval(self, tracker: APIUsageTracker) -> None:
        """Test should_sync before interval elapsed."""
        tracker._last_sync = time.time() - 100  # 100s ago, interval is 300s

        result = tracker.should_sync()

        assert result is False

    @pytest.mark.asyncio
    async def test_sync(self, tracker: APIUsageTracker, mock_cache: MagicMock) -> None:
        """Test sync updates tracker state."""
        tracker._cache = mock_cache
        tracker._remaining = 1000
        tracker._local_consumed = 50

        await tracker.sync(950)

        assert tracker._remaining == 950
        assert tracker._local_consumed == 0
        assert tracker._last_sync > 0

        # Should have saved to cache
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_warning_threshold_below(self, tracker: APIUsageTracker) -> None:
        """Test warning threshold when below threshold."""
        tracker._remaining = 500  # 5% of 10000 daily limit

        result = await tracker.check_warning_threshold()

        assert result is True  # 500 < 1000 (10% of 10000)

    @pytest.mark.asyncio
    async def test_check_warning_threshold_above(self, tracker: APIUsageTracker) -> None:
        """Test warning threshold when above threshold."""
        tracker._remaining = 5000  # 50% of 10000 daily limit

        result = await tracker.check_warning_threshold()

        assert result is False  # 5000 > 1000 (10% of 10000)

    async def test_get_stats(self, tracker: APIUsageTracker) -> None:
        """Test get_stats returns tracker state."""
        tracker._remaining = 1000
        tracker._local_consumed = 50
        tracker._last_sync = 12345.0

        stats = await tracker.get_stats()

        assert stats["enabled"] is True
        assert stats["remaining_estimate"] == 950
        assert stats["base_remaining"] == 1000
        assert stats["local_consumed"] == 50
        assert stats["last_sync"] == 12345.0
        assert stats["sync_interval_seconds"] == 300

    async def test_get_stats_never_synced(self, tracker: APIUsageTracker) -> None:
        """Test get_stats when never synced."""
        stats = await tracker.get_stats()

        assert stats["remaining_estimate"] is None
        assert stats["base_remaining"] is None
        assert stats["local_consumed"] == 0
        assert stats["last_sync"] is None


class TestAPIUsageTrackerDisabled:
    """Tests for disabled APIUsageTracker."""

    @pytest.fixture
    def disabled_config(self) -> UsageTrackerConfig:
        """Create a disabled configuration."""
        return UsageTrackerConfig(enabled=False)

    @pytest.fixture
    def tracker(self, disabled_config: UsageTrackerConfig) -> APIUsageTracker:
        """Create a disabled tracker."""
        return APIUsageTracker(disabled_config)

    @pytest.mark.asyncio
    async def test_decrement_noop(self, tracker: APIUsageTracker) -> None:
        """Test decrement is no-op when disabled."""
        await tracker.decrement()

        assert tracker._local_consumed == 0

    @pytest.mark.asyncio
    async def test_get_remaining_returns_none(self, tracker: APIUsageTracker) -> None:
        """Test get_remaining returns None when disabled."""
        tracker._remaining = 1000  # Even with value set

        result = await tracker.get_remaining()

        assert result is None

    def test_should_sync_returns_false(self, tracker: APIUsageTracker) -> None:
        """Test should_sync returns False when disabled."""
        result = tracker.should_sync()

        assert result is False

    @pytest.mark.asyncio
    async def test_sync_noop(self, tracker: APIUsageTracker) -> None:
        """Test sync is no-op when disabled."""
        await tracker.sync(1000)

        assert tracker._remaining is None


class TestNullUsageTracker:
    """Tests for NullUsageTracker."""

    @pytest.fixture
    def tracker(self) -> NullUsageTracker:
        """Create a null tracker."""
        return NullUsageTracker()

    @pytest.mark.asyncio
    async def test_initialize_noop(self, tracker: NullUsageTracker) -> None:
        """Test initialize is no-op."""
        mock_cache = MagicMock()
        await tracker.initialize(mock_cache)

        # Should not raise or have any effect

    @pytest.mark.asyncio
    async def test_decrement_noop(self, tracker: NullUsageTracker) -> None:
        """Test decrement is no-op."""
        await tracker.decrement()

        assert tracker._local_consumed == 0

    @pytest.mark.asyncio
    async def test_get_remaining_returns_none(self, tracker: NullUsageTracker) -> None:
        """Test get_remaining always returns None."""
        result = await tracker.get_remaining()

        assert result is None

    def test_should_sync_returns_false(self, tracker: NullUsageTracker) -> None:
        """Test should_sync always returns False."""
        result = tracker.should_sync()

        assert result is False

    @pytest.mark.asyncio
    async def test_sync_noop(self, tracker: NullUsageTracker) -> None:
        """Test sync is no-op."""
        await tracker.sync(1000)

        # Should not raise

    @pytest.mark.asyncio
    async def test_check_warning_threshold_returns_false(self, tracker: NullUsageTracker) -> None:
        """Test check_warning_threshold always returns False."""
        result = await tracker.check_warning_threshold()

        assert result is False

    async def test_get_stats(self, tracker: NullUsageTracker) -> None:
        """Test get_stats returns disabled status."""
        stats = await tracker.get_stats()

        assert stats["enabled"] is False
        assert stats["remaining_estimate"] is None


class TestAPIUsageTrackerConcurrency:
    """Tests for concurrent usage of APIUsageTracker."""

    @pytest.fixture
    def tracker(self) -> APIUsageTracker:
        """Create a test tracker."""
        config = UsageTrackerConfig(enabled=True)
        return APIUsageTracker(config)

    @pytest.mark.asyncio
    async def test_concurrent_decrements(self, tracker: APIUsageTracker) -> None:
        """Test concurrent decrements are thread-safe."""
        tracker._remaining = 10000

        # Run 100 concurrent decrements
        await asyncio.gather(*[tracker.decrement() for _ in range(100)])

        assert tracker._local_consumed == 100
        remaining = await tracker.get_remaining()
        assert remaining == 9900
