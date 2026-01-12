"""
Scheduler tasks for automated token updates and discovery.
"""
import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from src.ingestion.update_token import update_single_token
from src.ingestion.fetch_new_tokens import fetch_and_store_new_tokens
from src.scheduler.score_task import score_token_in_db
from src.utils.supabase_client import supabase
from src.alerts.alert_manager import alert_manager

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def _run_async(coro):
    """Run an async coroutine from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        asyncio.run(coro)


def update_all_tokens():
    """Update all tokens and check for alerts."""
    logger.info("Running scheduled token refresh...")

    result = supabase.table("tokens").select("mint_address").execute()
    tokens = result.data or []
    logger.info(f"Updating {len(tokens)} tokens")

    for row in tokens:
        mint = row["mint_address"]

        try:
            # Update token data
            update_single_token(mint)

            # Compute new scores
            score_token_in_db(mint)

            # Fetch updated token and check for alerts
            updated = supabase.table("tokens")\
                .select("*")\
                .eq("mint_address", mint)\
                .single()\
                .execute()

            if updated.data:
                _run_async(alert_manager.check_and_alert(updated.data))

        except Exception as e:
            logger.error(f"Failed to update {mint}: {e}")

    logger.info("Token refresh complete")


def discover_and_score_new_tokens():
    """Discover new tokens, score them, and send alerts."""
    logger.info("Checking for new tokens...")

    new_mints = fetch_and_store_new_tokens()

    if not new_mints:
        logger.info("No new tokens discovered")
        return

    logger.info(f"Discovered {len(new_mints)} new tokens")

    for mint in new_mints:
        try:
            # Score the new token
            score_token_in_db(mint)

            # Fetch token data and send alert
            token = supabase.table("tokens")\
                .select("*")\
                .eq("mint_address", mint)\
                .single()\
                .execute()

            if token.data:
                _run_async(alert_manager.alert_new_token(token.data))

        except Exception as e:
            logger.error(f"Failed to score new token {mint}: {e}")


def record_token_snapshots():
    """Record current token states for historical charts."""
    try:
        # Call the Supabase function to record snapshots
        supabase.rpc("record_token_snapshot").execute()
        logger.info("Recorded token snapshots for history")
    except Exception as e:
        logger.error(f"Failed to record snapshots: {e}")


def start_scheduler():
    """Initialize and start the background scheduler."""
    logger.info("Initializing scheduler...")

    # Update existing tokens every 30 mins
    scheduler.add_job(
        update_all_tokens,
        "interval",
        minutes=30,
        id="update_all_tokens",
        replace_existing=True
    )
    logger.info("Added job: update_all_tokens (30 min interval)")

    # Discover + score new tokens every 10 mins
    scheduler.add_job(
        discover_and_score_new_tokens,
        "interval",
        minutes=10,
        id="discover_new_tokens",
        replace_existing=True
    )
    logger.info("Added job: discover_and_score_new_tokens (10 min interval)")

    # Record snapshots every hour for charts
    scheduler.add_job(
        record_token_snapshots,
        "interval",
        hours=1,
        id="record_snapshots",
        replace_existing=True
    )
    logger.info("Added job: record_token_snapshots (1 hour interval)")

    scheduler.start()
    logger.info("Scheduler started successfully")
