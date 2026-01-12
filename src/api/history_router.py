"""
Token history API endpoints for price/liquidity charts.
"""
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import List
from src.utils.supabase_client import supabase

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{mint_address}")
def get_token_history(
    mint_address: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history (max 7 days)")
) -> List[dict]:
    """
    Get price/liquidity history for a token.

    Args:
        mint_address: Token mint address
        hours: Number of hours of history to retrieve (1-168)

    Returns:
        List of historical data points
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    result = supabase.table("token_history")\
        .select("price, liquidity, holder_count, composite_score, recorded_at")\
        .eq("mint_address", mint_address)\
        .gte("recorded_at", since.isoformat())\
        .order("recorded_at", desc=False)\
        .execute()

    return result.data or []


@router.get("/{mint_address}/latest")
def get_latest_history(mint_address: str, limit: int = Query(default=10, ge=1, le=100)) -> List[dict]:
    """
    Get the most recent history entries for a token.

    Args:
        mint_address: Token mint address
        limit: Number of entries to retrieve

    Returns:
        List of most recent historical data points
    """
    result = supabase.table("token_history")\
        .select("price, liquidity, holder_count, composite_score, recorded_at")\
        .eq("mint_address", mint_address)\
        .order("recorded_at", desc=True)\
        .limit(limit)\
        .execute()

    # Reverse to get chronological order
    data = result.data or []
    return list(reversed(data))


@router.get("/")
def get_all_history_summary(hours: int = Query(default=24, ge=1, le=168)) -> List[dict]:
    """
    Get a summary of price changes for all tokens over the specified period.

    Args:
        hours: Hours of history to analyze

    Returns:
        List of tokens with their price change summary
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    # Get current prices
    current = supabase.table("tokens")\
        .select("mint_address, symbol, name, price, liquidity")\
        .execute()

    current_data = {t["mint_address"]: t for t in (current.data or [])}

    # Get oldest price in the period for each token
    history = supabase.table("token_history")\
        .select("mint_address, price, recorded_at")\
        .gte("recorded_at", since.isoformat())\
        .order("recorded_at", desc=False)\
        .execute()

    # Group by mint and get first entry
    first_prices = {}
    for entry in (history.data or []):
        mint = entry["mint_address"]
        if mint not in first_prices:
            first_prices[mint] = entry["price"]

    # Calculate changes
    result = []
    for mint, token in current_data.items():
        old_price = first_prices.get(mint)
        new_price = token.get("price", 0)

        if old_price and old_price > 0:
            pct_change = ((new_price - old_price) / old_price) * 100
        else:
            pct_change = 0

        result.append({
            "mint_address": mint,
            "symbol": token.get("symbol"),
            "name": token.get("name"),
            "current_price": new_price,
            "old_price": old_price,
            "price_change_pct": round(pct_change, 2),
            "liquidity": token.get("liquidity", 0),
        })

    # Sort by absolute price change
    result.sort(key=lambda x: abs(x["price_change_pct"]), reverse=True)

    return result
