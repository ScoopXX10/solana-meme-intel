from src.utils.supabase_client import supabase
from src.ingestion.birdeye_client import get_token_price

def update_single_token(mint_address: str):
    data = get_token_price(mint_address)

    # If Birdeye fails or returns nothing, return False instead of None
    if not data:
        print(f"No data returned for {mint_address}")
        return False

    # Update Supabase
    supabase.table("tokens").update({
        "price": data.get("price"),
        "liquidity": data.get("liquidity"),
        "change_24h": data.get("change_24h"),
        "updated": data.get("updated"),
    }).eq("mint_address", mint_address).execute()

    print(f"Updated token: {mint_address}")
    return True   # <-- VERY IMPORTANT

