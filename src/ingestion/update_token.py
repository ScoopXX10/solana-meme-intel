"""
Token data updater - fetches price, liquidity, and metadata from external APIs.
"""
import logging
from typing import Dict, Any, Optional, Tuple

from src.utils.http_client import APIClient
from src.utils.supabase_client import supabase
from src.utils.helius_client import HELIUS_API_KEY

logger = logging.getLogger(__name__)

# Initialize API clients
dexscreener_client = APIClient(base_url="https://api.dexscreener.com")
helius_client = APIClient(
    base_url="https://api.helius.xyz",
    headers={"Content-Type": "application/json"},
)


def get_price_liquidity(mint: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Fetch price and liquidity from DexScreener API.

    Args:
        mint: Token mint address

    Returns:
        Tuple of (price, liquidity_usd) or (None, None) on failure
    """
    try:
        data = dexscreener_client.get(f"/latest/dex/tokens/{mint}")
        pairs = data.get("pairs", [])

        if not pairs:
            logger.warning(f"No trading pairs found for {mint}")
            return None, None

        # Select pair with highest liquidity
        best = max(pairs, key=lambda p: p.get("liquidity", {}).get("usd", 0))
        price = best.get("priceUsd")
        liquidity = best.get("liquidity", {}).get("usd")

        if price is None:
            logger.warning(f"No price in DexScreener response for {mint}")
            return None, None

        logger.debug(f"DexScreener: {mint[:8]}... price=${price}, liq=${liquidity}")
        return float(price), float(liquidity or 0)

    except Exception as e:
        logger.error(f"DexScreener API error for {mint}: {e}")
        return None, None


def get_metadata(mint: str) -> Dict[str, Any]:
    """
    Fetch token metadata from Helius API.

    Args:
        mint: Token mint address

    Returns:
        Dict with name, symbol, and holder count
    """
    default = {"name": None, "symbol": None, "holders": 0}

    try:
        data = helius_client.post(
            f"/v0/tokens/metadata?api-key={HELIUS_API_KEY}",
            json={"mintAccounts": [mint]}
        )

        if not isinstance(data, list) or not data:
            logger.warning(f"Empty Helius response for {mint}")
            return default

        token_data = data[0]
        on_chain = token_data.get("onChainData", {})
        off_chain = token_data.get("offChainData", {})

        name = on_chain.get("name") or off_chain.get("metadata", {}).get("name")
        symbol = on_chain.get("symbol") or off_chain.get("metadata", {}).get("symbol")
        holders = token_data.get("owners", 0)

        logger.debug(f"Helius metadata: {symbol} ({name}), {holders} holders")
        return {"name": name, "symbol": symbol, "holders": holders}

    except Exception as e:
        logger.error(f"Helius metadata error for {mint}: {e}")
        return default


def update_single_token(mint_address: str) -> Dict[str, Any]:
    """
    Update a single token's data from external APIs and save to database.

    Args:
        mint_address: Token mint address

    Returns:
        Dict with update status and data
    """
    logger.info(f"Updating token: {mint_address[:12]}...")

    result = {
        "mint_address": mint_address,
        "success": False,
        "price_updated": False,
        "metadata_updated": False,
        "data": {},
        "error": None,
    }

    try:
        # Fetch price and liquidity
        price, liquidity = get_price_liquidity(mint_address)

        # Fetch metadata
        meta = get_metadata(mint_address)

        # Build update payload
        update_payload = {}

        if price is not None:
            update_payload["price"] = price
            update_payload["liquidity"] = liquidity
            result["price_updated"] = True

        if meta["name"] or meta["symbol"]:
            update_payload["name"] = meta["name"]
            update_payload["symbol"] = meta["symbol"]
            result["metadata_updated"] = True

        if meta["holders"]:
            update_payload["holder_count"] = meta["holders"]

        # Only update if we have data
        if update_payload:
            update_payload["updated"] = "now()"

            supabase.table("tokens")\
                .update(update_payload)\
                .eq("mint_address", mint_address)\
                .execute()

            result["success"] = True
            result["data"] = update_payload
            logger.info(f"Updated {mint_address[:8]}...: price=${price}, liq=${liquidity}")
        else:
            logger.warning(f"No data to update for {mint_address}")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Failed to update {mint_address}: {e}")

    return result


def get_token_authorities(mint: str) -> Dict[str, str]:
    """
    Get mint and freeze authority status from on-chain data.

    Args:
        mint: Token mint address

    Returns:
        Dict with mint_auth and freeze_auth status
    """
    from src.utils.helius_client import helius_rpc

    default = {"mint_auth": "unknown", "freeze_auth": "unknown"}

    try:
        result = helius_rpc("getAccountInfo", [mint, {"encoding": "jsonParsed"}])

        if not result or "value" not in result or result["value"] is None:
            return default

        data = result["value"].get("data", {})
        if not isinstance(data, dict):
            return default

        parsed = data.get("parsed", {})
        info = parsed.get("info", {})

        mint_auth = info.get("mintAuthority")
        freeze_auth = info.get("freezeAuthority")

        return {
            "mint_auth": "renounced" if mint_auth is None else "active",
            "freeze_auth": "renounced" if freeze_auth is None else "active",
        }

    except Exception as e:
        logger.error(f"Failed to get authorities for {mint}: {e}")
        return default
