"""
Reward System Plugin for ANSE

Implements a motivation loop and reward tracking for reinforcement learning.
Agents can receive rewards/penalties and accumulate them over time.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RewardSystemPlugin:
    """Reward tracking and motivation loop."""

    name = "reward_system"
    description = "Motivation loop and reward tracking for reinforcement learning"
    version = "1.0.0"

    def __init__(self):
        """Initialize reward system."""
        self.total_reward: float = 0.0
        self.reward_count: int = 0
        self.reward_history: List[Dict[str, Any]] = []
        self.reward_threshold: float = 0.0

    async def reward(
        self,
        value: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Give the agent a reward or penalty.

        Args:
            value: Reward value (positive = reward, negative = penalty)
            reason: Optional string explaining the reward

        Returns:
            Dict with reward confirmation and new total
        """
        value = float(value)
        self.total_reward += value
        self.reward_count += 1

        event = {
            "value": value,
            "reason": reason or "unspecified",
            "timestamp": datetime.now().isoformat(),
            "total_at_time": self.total_reward,
            "event_number": self.reward_count
        }
        self.reward_history.append(event)

        # Keep only last 100 events
        if len(self.reward_history) > 100:
            self.reward_history.pop(0)

        logger.info(f"[REWARD] +{value} ({reason or 'unspecified'}) -> Total: {self.total_reward}")

        threshold_met = self.is_goal_achieved()

        return {
            "status": "success",
            "reward_given": value,
            "total_reward": self.total_reward,
            "goal_achieved": threshold_met,
            "timestamp": event["timestamp"]
        }

    async def get_reward_total(self) -> Dict[str, Any]:
        """
        Get total accumulated reward.

        Returns:
            Dict with total, count, and average
        """
        average = self.total_reward / self.reward_count if self.reward_count > 0 else 0.0

        return {
            "status": "success",
            "total_reward": self.total_reward,
            "reward_count": self.reward_count,
            "average_reward": average,
            "goal_achieved": self.is_goal_achieved()
        }

    async def reset_rewards(self) -> Dict[str, Any]:
        """
        Reset reward accumulator to zero.

        Returns:
            Confirmation dict
        """
        old_total = self.total_reward
        self.total_reward = 0.0
        self.reward_count = 0
        self.reward_history.clear()

        logger.info(f"[REWARD] Reset rewards (was {old_total})")

        return {
            "status": "success",
            "message": "Rewards reset",
            "previous_total": old_total
        }

    async def get_reward_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent reward events.

        Args:
            limit: Maximum number of events to return

        Returns:
            Dict with reward history array
        """
        limit = max(1, min(limit, 100))  # Clamp to 1-100
        recent = self.reward_history[-limit:]

        return {
            "status": "success",
            "limit": limit,
            "count": len(recent),
            "history": recent
        }

    async def set_reward_threshold(self, threshold: float) -> Dict[str, Any]:
        """
        Set minimum reward threshold for goal achievement.

        Args:
            threshold: Target reward value

        Returns:
            Confirmation dict
        """
        threshold = float(threshold)
        old_threshold = self.reward_threshold
        self.reward_threshold = threshold

        logger.info(f"[REWARD] Threshold set to {threshold} (was {old_threshold})")

        return {
            "status": "success",
            "threshold": threshold,
            "previous_threshold": old_threshold,
            "goal_achieved": self.is_goal_achieved()
        }

    def is_goal_achieved(self) -> bool:
        """
        Check if reward threshold has been met.

        Returns:
            True if total_reward >= threshold
        """
        if self.reward_threshold == 0.0:
            return False
        return self.total_reward >= self.reward_threshold
