"""
On-chain data fetching for token scoring.
Fetches real data from Solana via Helius RPC for:
- Mint/Freeze authority status (Risk Score)
- Holder distribution and whale concentration (Holder Score)
"""
import logging
from typing import Dict, Any, Optional, List
from src.utils.helius_client import helius_rpc, HELIUS_API_KEY
import requests

logger = logging.getLogger(__name__)


def get_token_authority_status(mint_address: str) -> Dict[str, str]:
    """
    Fetch mint and freeze authority status from on-chain token data.

    Args:
        mint_address: Token mint address

    Returns:
        Dict with mint_auth and freeze_auth status:
        - "renounced" = authority is None (safe)
        - "active" = authority exists (risky)
        - "unknown" = couldn't fetch data
    """
    result = {
        "mint_auth": "unknown",
        "freeze_auth": "unknown"
    }

    try:
        # Use getAccountInfo with jsonParsed encoding to get token mint data
        response = helius_rpc("getAccountInfo", [
            mint_address,
            {"encoding": "jsonParsed"}
        ])

        if not response or not response.get("value"):
            logger.warning(f"No account info for {mint_address}")
            return result

        value = response["value"]
        data = value.get("data")

        if not data or not isinstance(data, dict):
            logger.warning(f"Unexpected data format for {mint_address}")
            return result

        parsed = data.get("parsed", {})
        info = parsed.get("info", {})

        # Check mint authority
        mint_authority = info.get("mintAuthority")
        if mint_authority is None:
            result["mint_auth"] = "renounced"
        else:
            result["mint_auth"] = "active"

        # Check freeze authority
        freeze_authority = info.get("freezeAuthority")
        if freeze_authority is None:
            result["freeze_auth"] = "renounced"
        else:
            result["freeze_auth"] = "active"

        logger.debug(f"Authority status for {mint_address[:8]}...: mint={result['mint_auth']}, freeze={result['freeze_auth']}")

    except Exception as e:
        logger.error(f"Failed to get authority status for {mint_address}: {e}")

    return result


def get_token_largest_accounts(mint_address: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch the largest token holders for a given mint.

    Args:
        mint_address: Token mint address
        limit: Max number of accounts to return

    Returns:
        List of dicts with address and amount for top holders
    """
    try:
        response = helius_rpc("getTokenLargestAccounts", [mint_address])

        if not response or not response.get("value"):
            logger.warning(f"No largest accounts for {mint_address}")
            return []

        accounts = response["value"][:limit]

        return [
            {
                "address": acc.get("address"),
                "amount": int(acc.get("amount", 0)),
                "decimals": acc.get("decimals", 0),
                "ui_amount": float(acc.get("uiAmount", 0) or 0)
            }
            for acc in accounts
        ]

    except Exception as e:
        logger.error(f"Failed to get largest accounts for {mint_address}: {e}")
        return []


def get_token_supply(mint_address: str) -> Optional[int]:
    """
    Fetch the total supply of a token.

    Args:
        mint_address: Token mint address

    Returns:
        Total supply as integer, or None if failed
    """
    try:
        response = helius_rpc("getTokenSupply", [mint_address])

        if not response or not response.get("value"):
            return None

        return int(response["value"].get("amount", 0))

    except Exception as e:
        logger.error(f"Failed to get token supply for {mint_address}: {e}")
        return None


def calculate_holder_metrics(mint_address: str) -> Dict[str, Any]:
    """
    Calculate holder distribution metrics for scoring.

    Args:
        mint_address: Token mint address

    Returns:
        Dict with:
        - holder_count: Estimated number of holders
        - top_holder_pct: % held by top 1 holder
        - top10_pct: % held by top 10 holders
        - whale_count: Number of wallets holding > 1% of supply
        - gini: Gini coefficient (0-1, lower is more equal)
    """
    result = {
        "holder_count": 0,
        "top_holder_pct": 100.0,
        "top10_pct": 100.0,
        "whale_count": 0,
        "gini": 1.0  # Default to worst case
    }

    try:
        # Get largest accounts
        largest = get_token_largest_accounts(mint_address, limit=20)

        if not largest:
            logger.warning(f"No holder data for {mint_address}")
            return result

        # Get total supply
        total_supply = get_token_supply(mint_address)

        if not total_supply or total_supply == 0:
            logger.warning(f"No supply data for {mint_address}")
            return result

        # Calculate metrics
        amounts = [acc["amount"] for acc in largest]

        # Top holder percentage
        if amounts:
            result["top_holder_pct"] = (amounts[0] / total_supply) * 100

        # Top 10 percentage
        top10_amount = sum(amounts[:10])
        result["top10_pct"] = (top10_amount / total_supply) * 100

        # Whale count (holders with > 1% of supply)
        whale_threshold = total_supply * 0.01
        result["whale_count"] = sum(1 for amt in amounts if amt > whale_threshold)

        # Estimate holder count using Helius DAS API
        holder_count = get_holder_count_das(mint_address)
        if holder_count:
            result["holder_count"] = holder_count
        else:
            # Fallback: estimate based on top holders
            # If top 20 hold less than 80%, there are likely many more holders
            top20_pct = (sum(amounts) / total_supply) * 100
            if top20_pct < 50:
                result["holder_count"] = 5000  # Many holders
            elif top20_pct < 70:
                result["holder_count"] = 1000
            elif top20_pct < 90:
                result["holder_count"] = 250
            else:
                result["holder_count"] = 50

        # Calculate Gini coefficient from top holders
        result["gini"] = calculate_gini(amounts)

        logger.info(
            f"Holder metrics for {mint_address[:8]}...: "
            f"holders={result['holder_count']}, top1={result['top_holder_pct']:.1f}%, "
            f"top10={result['top10_pct']:.1f}%, whales={result['whale_count']}"
        )

    except Exception as e:
        logger.error(f"Failed to calculate holder metrics for {mint_address}: {e}")

    return result


def get_holder_count_das(mint_address: str) -> Optional[int]:
    """
    Get holder count using Helius DAS (Digital Asset Standard) API.

    Args:
        mint_address: Token mint address

    Returns:
        Number of holders, or None if failed
    """
    try:
        # Use Helius DAS API to get token holders
        url = f"https://api.helius.xyz/v0/token-metadata?api-key={HELIUS_API_KEY}"

        response = requests.post(
            url,
            json={"mintAccounts": [mint_address]},
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data and isinstance(data, list) and len(data) > 0:
            # Some Helius responses include holder count
            return data[0].get("onChainData", {}).get("holders") or \
                   data[0].get("owners")

        return None

    except Exception as e:
        logger.debug(f"DAS holder count failed for {mint_address}: {e}")
        return None


def calculate_gini(amounts: List[int]) -> float:
    """
    Calculate Gini coefficient from a list of holder amounts.

    Args:
        amounts: List of token amounts held

    Returns:
        Gini coefficient (0 = perfect equality, 1 = perfect inequality)
    """
    if not amounts or len(amounts) < 2:
        return 1.0

    # Sort amounts
    sorted_amounts = sorted(amounts)
    n = len(sorted_amounts)

    # Calculate Gini using the relative mean absolute difference formula
    total = sum(sorted_amounts)
    if total == 0:
        return 1.0

    # Cumulative sum approach
    cumsum = 0
    for i, amt in enumerate(sorted_amounts):
        cumsum += (2 * (i + 1) - n - 1) * amt

    gini = cumsum / (n * total)

    # Clamp to 0-1
    return max(0.0, min(1.0, gini))


def fetch_all_scoring_data(mint_address: str) -> Dict[str, Any]:
    """
    Fetch all on-chain data needed for scoring a token.

    Args:
        mint_address: Token mint address

    Returns:
        Dict with all scoring-relevant data:
        - mint_auth: Authority status
        - freeze_auth: Authority status
        - holder_count: Number of holders
        - top_holder_pct: Top 1 holder percentage
        - top10_pct: Top 10 holder percentage
        - whale_count: Number of whales
        - gini: Distribution inequality
    """
    logger.info(f"Fetching scoring data for {mint_address[:12]}...")

    # Get authority status
    auth_status = get_token_authority_status(mint_address)

    # Get holder metrics
    holder_metrics = calculate_holder_metrics(mint_address)

    # Combine all data
    return {
        "mint_auth": auth_status["mint_auth"],
        "freeze_auth": auth_status["freeze_auth"],
        "holder_count": holder_metrics["holder_count"],
        "top_holder_pct": holder_metrics["top_holder_pct"],
        "top10_pct": holder_metrics["top10_pct"],
        "whale_count": holder_metrics["whale_count"],
        "gini": holder_metrics["gini"],
    }
