"""
Alert manager - tracks token state changes and triggers alerts.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from src.alerts.telegram_bot import telegram_service

logger = logging.getLogger(__name__)

# Alert thresholds (configurable)
SCORE_CHANGE_THRESHOLD = 5.0  # Points
PRICE_CHANGE_THRESHOLD = 10.0  # Percentage
LIQUIDITY_CHANGE_THRESHOLD = 20.0  # Percentage


class AlertManager:
    """
    Manages alert state and triggers notifications when thresholds are exceeded.
    Tracks previous token states to detect changes.
    """

    def __init__(self):
        self._previous_states: Dict[str, Dict[str, Any]] = {}

    def _get_previous_state(self, mint: str) -> Optional[Dict[str, Any]]:
        """Get the previous state for a token."""
        return self._previous_states.get(mint)

    def _save_state(self, mint: str, state: Dict[str, Any]) -> None:
        """Save the current state for future comparison."""
        self._previous_states[mint] = state

    async def check_and_alert(self, token: Dict[str, Any]) -> None:
        """
        Check token for alert conditions and send notifications.

        Args:
            token: Token data dict from database
        """
        mint = token.get("mint_address")
        if not mint:
            return

        previous = self._get_previous_state(mint)

        if previous:
            # Check for score changes
            await self._check_score_change(token, previous)

            # Check for price changes
            await self._check_price_change(token, previous)

            # Check for liquidity changes
            await self._check_liquidity_change(token, previous)

        # Save current state for next comparison
        self._save_state(mint, {
            "composite_score": token.get("composite_score", 0),
            "price": token.get("price", 0),
            "liquidity": token.get("liquidity", 0),
        })

    async def _check_score_change(
        self,
        token: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> None:
        """Check for significant score changes."""
        old_score = previous.get("composite_score", 0) or 0
        new_score = token.get("composite_score", 0) or 0

        if abs(new_score - old_score) >= SCORE_CHANGE_THRESHOLD:
            logger.info(
                f"Score change alert: {token.get('symbol')} "
                f"{old_score:.1f} -> {new_score:.1f}"
            )
            await telegram_service.send_score_change_alert(token, old_score, new_score)

    async def _check_price_change(
        self,
        token: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> None:
        """Check for significant price changes."""
        old_price = previous.get("price", 0) or 0
        new_price = token.get("price", 0) or 0

        if old_price > 0:
            pct_change = ((new_price - old_price) / old_price) * 100

            if abs(pct_change) >= PRICE_CHANGE_THRESHOLD:
                logger.info(
                    f"Price change alert: {token.get('symbol')} "
                    f"${old_price:.8f} -> ${new_price:.8f} ({pct_change:+.1f}%)"
                )
                await telegram_service.send_price_alert(
                    token, old_price, new_price, pct_change
                )

    async def _check_liquidity_change(
        self,
        token: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> None:
        """Check for significant liquidity changes."""
        old_liq = previous.get("liquidity", 0) or 0
        new_liq = token.get("liquidity", 0) or 0

        if old_liq > 0:
            pct_change = ((new_liq - old_liq) / old_liq) * 100

            if abs(pct_change) >= LIQUIDITY_CHANGE_THRESHOLD:
                logger.info(
                    f"Liquidity change alert: {token.get('symbol')} "
                    f"${old_liq:,.0f} -> ${new_liq:,.0f} ({pct_change:+.1f}%)"
                )
                await telegram_service.send_liquidity_alert(
                    token, old_liq, new_liq, pct_change
                )

    async def alert_new_token(self, token: Dict[str, Any]) -> None:
        """
        Send alert for newly discovered token.

        Args:
            token: Token data dict from database
        """
        logger.info(f"New token alert: {token.get('symbol')} ({token.get('mint_address', '')[:8]}...)")
        await telegram_service.send_new_token_alert(token)

        # Save initial state
        mint = token.get("mint_address")
        if mint:
            self._save_state(mint, {
                "composite_score": token.get("composite_score", 0),
                "price": token.get("price", 0),
                "liquidity": token.get("liquidity", 0),
            })


def run_async(coro):
    """Helper to run async functions from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop (e.g., in Jupyter), use it
            asyncio.ensure_future(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create a new one
        asyncio.run(coro)


# Global singleton instance
alert_manager = AlertManager()
