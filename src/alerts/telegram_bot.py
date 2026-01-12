"""
Telegram bot service for sending alerts.
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


class TelegramAlertService:
    """
    Service for sending alerts via Telegram bot.
    Uses python-telegram-bot library for async messaging.
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self._bot = None

    @property
    def is_configured(self) -> bool:
        """Check if Telegram credentials are configured."""
        return bool(self.bot_token and self.chat_id)

    async def _get_bot(self):
        """Lazy-load the Telegram bot instance."""
        if self._bot is None:
            try:
                from telegram import Bot
                self._bot = Bot(token=self.bot_token)
            except ImportError:
                logger.error("python-telegram-bot not installed. Run: pip install python-telegram-bot")
                return None
        return self._bot

    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message via Telegram.

        Args:
            message: Message text (supports HTML formatting)
            parse_mode: Parse mode (HTML or Markdown)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning("Telegram not configured, skipping alert")
            return False

        try:
            bot = await self._get_bot()
            if bot is None:
                return False

            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
            )
            logger.debug("Telegram message sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def send_new_token_alert(self, token: Dict[str, Any]) -> bool:
        """Send alert for newly discovered token."""
        symbol = token.get("symbol") or "???"
        name = token.get("name") or "Unknown"
        mint = token.get("mint_address", "")
        price = token.get("price", 0)
        liquidity = token.get("liquidity", 0)

        message = f"""
🆕 <b>New Token Discovered</b>

<b>Name:</b> {name}
<b>Symbol:</b> {symbol}
<b>Mint:</b> <code>{mint}</code>
<b>Price:</b> ${price:.8f}
<b>Liquidity:</b> ${liquidity:,.0f}
"""
        return await self.send_message(message.strip())

    async def send_score_change_alert(
        self,
        token: Dict[str, Any],
        old_score: float,
        new_score: float
    ) -> bool:
        """Send alert for significant score change."""
        direction = "📈" if new_score > old_score else "📉"
        change = new_score - old_score
        symbol = token.get("symbol") or "???"
        name = token.get("name") or "Unknown"
        price = token.get("price", 0)

        message = f"""
{direction} <b>Score Change Alert</b>

<b>Token:</b> {symbol} ({name})
<b>Score:</b> {old_score:.1f} → {new_score:.1f} ({change:+.1f})
<b>Price:</b> ${price:.8f}

<b>Breakdown:</b>
• Dev: {token.get('dev_score', 0):.0f}
• Holder: {token.get('holder_score', 0):.0f}
• Risk: {token.get('risk_score', 0):.0f}
• Meme: {token.get('meme_score', 0):.0f}
"""
        return await self.send_message(message.strip())

    async def send_price_alert(
        self,
        token: Dict[str, Any],
        old_price: float,
        new_price: float,
        pct_change: float
    ) -> bool:
        """Send alert for significant price change."""
        direction = "🚀" if pct_change > 0 else "💥"
        symbol = token.get("symbol") or "???"
        liquidity = token.get("liquidity", 0)

        message = f"""
{direction} <b>Price Alert</b>

<b>Token:</b> {symbol}
<b>Price:</b> ${old_price:.8f} → ${new_price:.8f}
<b>Change:</b> {pct_change:+.1f}%
<b>Liquidity:</b> ${liquidity:,.0f}
"""
        return await self.send_message(message.strip())

    async def send_liquidity_alert(
        self,
        token: Dict[str, Any],
        old_liq: float,
        new_liq: float,
        pct_change: float
    ) -> bool:
        """Send alert for significant liquidity change."""
        direction = "💰" if pct_change > 0 else "⚠️"
        symbol = token.get("symbol") or "???"

        message = f"""
{direction} <b>Liquidity Alert</b>

<b>Token:</b> {symbol}
<b>Liquidity:</b> ${old_liq:,.0f} → ${new_liq:,.0f}
<b>Change:</b> {pct_change:+.1f}%
"""
        return await self.send_message(message.strip())


# Global singleton instance
telegram_service = TelegramAlertService()
