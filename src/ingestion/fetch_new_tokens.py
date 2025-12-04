import requests
from src.utils.supabase_client import supabase

BIRDEYE_URL = "https://public-api.birdeye.so/solana/tokens/list?limit=50"
HEADERS = {"X-API-KEY": "<YOUR_KEY>"}

def fetch_and_store_new_tokens():
    try:
        resp = requests.get(BIRDEYE_URL, headers=HEADERS, timeout=10)
        data = resp.json()

        tokens = data.get("data", [])
        added = 0

        for t in tokens:
            mint = t.get("address")

            # Check if exists
            existing = supabase.table("tokens").select("mint_address")\
                .eq("mint_address", mint).execute()

            if existing.data:
                continue  # already exists

            # Insert new token row
            supabase.table("tokens").insert({
                "mint_address": mint,
                "symbol": t.get("symbol"),
                "name": t.get("name"),
                "price": t.get("price", 0),
                "liq_pct": 0,  # to be filled by update_single_token
            }).execute()

            added += 1

        print(f"🆕 Added {added} new tokens.")

    except Exception as e:
        print("Fetch error:", e)
