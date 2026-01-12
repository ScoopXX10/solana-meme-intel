"""
Alerts module - handles notifications via Telegram and other channels.
"""
from src.alerts.telegram_bot import telegram_service
from src.alerts.alert_manager import alert_manager

__all__ = ["telegram_service", "alert_manager"]
