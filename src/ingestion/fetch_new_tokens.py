import os
import logging
from typing import List
from dotenv import load_dotenv
import requests
from src.utils.supabase_client import supabase

load_dotenv()
logger = logging.getLogger(__name__)

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
BIRDEYE_URL = "https://public-api.birdeye.so/defi/tokenlist"


def fetch_and_store_new_tokens() -> List[str]:
    """
    Fetch new tokens from Birdeye and store in database.
    Returns list of newly added mint addresses.
    """
    if not BIRDEYE_API_KEY:
        logger.warning("BIRDEYE_API_KEY not configured, skipping token discovery")
        return []

    headers = {
        "X-API-KEY": BIRDEYE_API_KEY,
        "x-chain": "solana",
        "accept": "application/json"
    }

    new_mints = []

    try:
        resp = requests.get(
            BIRDEYE_URL,
            headers=headers,
            params={"sort_by": "v24hUSD", "sort_type": "desc", "limit": 50},
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()

        tokens = data.get("data", {}).get("tokens", [])

        if not tokens:
            logger.info("No tokens returned from Birdeye")
            return []

        for t in tokens:
            mint = t.get("address")
            if not mint:
                continue

            # Check if already exists
            existing = supabase.table("tokens").select("mint_address")\
                .eq("mint_address", mint).execute()

            if existing.data:
                continue

            # Insert new token row
            try:
                supabase.table("tokens").insert({
                    "mint_address": mint,
                    "symbol": t.get("symbol"),
                    "name": t.get("name"),
                    "price": t.get("price", 0),
                    "liquidity": t.get("liquidity", 0),
                }).execute()

                new_mints.append(mint)
                logger.info(f"Added new token: {t.get('symbol')} ({mint[:8]}...)")

            except Exception as insert_err:
                logger.error(f"Failed to insert {mint}: {insert_err}")

        logger.info(f"Added {len(new_mints)} new tokens")

    except requests.exceptions.RequestException as e:
        logger.error(f"Birdeye API error: {e}")
    except Exception as e:
        logger.error(f"Fetch error: {e}")

    return new_mints
