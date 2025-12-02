from src.utils.supabase_client import supabase
from src.ingestion.birdeye_client import get_token_price

def update_single_token(mint_address: str):
    data = get_token_price(mint_address)

    if data:
        supabase.table("tokens").update({
            "price": data["price"],
            "liquidity": data["liquidity"],
            "change_24h": data["change_24h"],
            "updated": data["updated"]
        }).eq("mint_address", mint_address).execute()

        print(f"Updated token: {mint_address}")
    else:
        print(f"No data returned for {mint_address}")
