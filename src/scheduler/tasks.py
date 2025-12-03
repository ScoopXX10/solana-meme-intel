from apscheduler.schedulers.background import BackgroundScheduler
from src.ingestion.update_token import update_single_token
from src.utils.supabase_client import supabase

scheduler = BackgroundScheduler()

def update_all_tokens():
    print("⏰ Scheduled job triggered: updating tokens...")

    result = supabase.table("tokens").select("mint_address").execute()
    tokens = result.data or []

    if not tokens:
        print("⚠️ No tokens found to update.")
        return

    for row in tokens:
        mint = row["mint_address"]
        print(f"🔄 Updating {mint}")
        update_single_token(mint)

    print("✅ Token update cycle complete.")

def start_scheduler():
    print("🔥 Initializing scheduler...")

    # Runs every 5 minutes for testing
    scheduler.add_job(update_all_tokens, "interval", minutes=5)

    scheduler.start()
    print("✅ Scheduler started successfully.")
