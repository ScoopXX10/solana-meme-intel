from apscheduler.schedulers.background import BackgroundScheduler
from src.ingestion.update_token import update_single_token
from src.ingestion.fetch_new_tokens import fetch_and_store_new_tokens
from src.scheduler.score_task import score_token_in_db
from src.utils.supabase_client import supabase

scheduler = BackgroundScheduler()

def update_all_tokens():
    print("🔄 Running scheduled token refresh...")

    result = supabase.table("tokens").select("mint_address").execute()
    tokens = result.data or []

    for row in tokens:
        mint = row["mint_address"]

        print(f"   → updating {mint}")
        update_single_token(mint)

        print(f"   → scoring {mint}")
        score_token_in_db(mint)


def discover_and_score_new_tokens():
    print("🆕 Checking for new tokens...")

    new_mints = fetch_and_store_new_tokens()

    if not new_mints:
        print("   → No new tokens discovered.")
        return

    for mint in new_mints:
        print(f"   → scoring NEW token {mint}")
        score_token_in_db(mint)


def start_scheduler():
    print("🔥 Initializing scheduler...")

    # Update existing tokens every 30 mins
    scheduler.add_job(update_all_tokens, "interval", minutes=30)
    print("🧪 Added job: update_all_tokens (30 min interval)")

    # Discover + score new tokens every 10 mins
    scheduler.add_job(discover_and_score_new_tokens, "interval", minutes=10)
    print("🧪 Added job: discover_and_score_new_tokens (10 min interval)")

    scheduler.start()
    print("✅ Scheduler started successfully.")
