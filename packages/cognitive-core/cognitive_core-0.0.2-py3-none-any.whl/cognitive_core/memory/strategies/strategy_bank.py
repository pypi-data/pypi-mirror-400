"""Strategy protocols for StrategyBank."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cognitive_core.core.types import Strategy, Trajectory


@runtime_checkable
class StrategyAbstractor(Protocol):
    """Abstracts a trajectory into a reusable strategy."""

    async def abstract(self, trajectory: Trajectory) -> Strategy | None:
        """Extract high-level strategy. Returns None if not abstractable."""
        ...


@runtime_checkable
class SuccessRateUpdater(Protocol):
    """Updates success rate statistics for strategies."""

    def update(
        self,
        current_rate: float,
        current_count: int,
        success: bool,
    ) -> tuple[float, int]:
        """Return (new_rate, new_count)."""
        ...


# Default implementations


class EMASuccessUpdater:
    """Exponential moving average for success rate."""

    def __init__(self, alpha: float = 0.1):
        """Initialize with smoothing factor alpha.

        Args:
            alpha: Smoothing factor (0 < alpha <= 1). Higher values give more
                   weight to recent observations.
        """
        self.alpha = alpha

    def update(
        self,
        current_rate: float,
        current_count: int,
        success: bool,
    ) -> tuple[float, int]:
        """Update success rate using exponential moving average.

        Args:
            current_rate: Current success rate
            current_count: Current observation count
            success: Whether the latest attempt succeeded

        Returns:
            Tuple of (new_rate, new_count)
        """
        new_value = 1.0 if success else 0.0
        new_rate = self.alpha * new_value + (1 - self.alpha) * current_rate
        return (new_rate, current_count + 1)


class SimpleAverageUpdater:
    """Simple running average (baseline)."""

    def update(
        self,
        current_rate: float,
        current_count: int,
        success: bool,
    ) -> tuple[float, int]:
        """Update success rate using simple running average.

        Args:
            current_rate: Current success rate
            current_count: Current observation count
            success: Whether the latest attempt succeeded

        Returns:
            Tuple of (new_rate, new_count)
        """
        new_count = current_count + 1
        total_successes = current_rate * current_count + (1.0 if success else 0.0)
        new_rate = total_successes / new_count
        return (new_rate, new_count)
