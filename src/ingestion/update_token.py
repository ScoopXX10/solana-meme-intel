import requests
from src.utils.supabase_client import supabase
from src.utils.helius_client import HELIUS_API_KEY


# ---------------------------------------------------------
# DexScreener Price + Liquidity (Correct Endpoint)
# ---------------------------------------------------------
def get_price_liquidity(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        r = requests.get(url, timeout=10).json()

        pairs = r.get("pairs", [])

        if not pairs:
            print(f"[DexScreener] No pairs found for {mint}")
            return None, None

        best = max(pairs, key=lambda p: p.get("liquidity", {}).get("usd", 0))
        price = best.get("priceUsd")
        liquidity = best.get("liquidity", {}).get("usd")

        if price is None:
            return None, None

        return float(price), float(liquidity or 0)

    except Exception:
        return None, None


# ---------------------------------------------------------
# Helius Metadata (Best endpoint)
# ---------------------------------------------------------
def get_metadata(mint):
    try:
        url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={HELIUS_API_KEY}"

        payload = {"mintAccounts": [mint]}
        r = requests.post(url, json=payload, timeout=10).json()

        if not isinstance(r, list) or not r:
            return {"name": None, "symbol": None, "holders": 0}

        meta = r[0].get("onChainData", {})
        off = r[0].get("offChainData", {})

        return {
            "name": meta.get("name") or off.get("metadata", {}).get("name"),
            "symbol": meta.get("symbol") or off.get("metadata", {}).get("symbol"),
            "holders": r[0].get("owners", 0)
        }

    except Exception as e:
        print(f"[Helius Metadata Error] {e}")
        return {"name": None, "symbol": None, "holders": 0}


# ---------------------------------------------------------
# MAIN UPDATER
# ---------------------------------------------------------
def update_single_token(mint_address: str):
    print(f"🔄 Updating {mint_address}")

    price, liquidity = get_price_liquidity(mint_address)
    if price is None:
        print(f"⚠️ No price available for {mint_address}")
        return False

    meta = get_metadata(mint_address)

    update_payload = {
        "price": price,
        "liquidity": liquidity,
        "holder_count": meta["holders"],
        "name": meta["name"],
        "symbol": meta["symbol"],
        "updated": "now()"
    }

    supabase.table("tokens")\
        .update(update_payload)\
        .eq("mint_address", mint_address)\
        .execute()

    print(f"✅ Updated {mint_address}: {update_payload}")
    return update_payload
