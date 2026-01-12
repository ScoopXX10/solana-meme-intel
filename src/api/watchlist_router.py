"""
Watchlist API endpoints for managing user token watchlists.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.utils.supabase_client import supabase

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAddRequest(BaseModel):
    """Request body for adding a token to watchlist."""
    mint_address: str
    notes: Optional[str] = None


class WatchlistItem(BaseModel):
    """Response model for a watchlist item."""
    id: str
    user_id: str
    mint_address: str
    added_at: str
    notes: Optional[str] = None


@router.get("/{user_id}")
def get_watchlist(user_id: str) -> List[dict]:
    """
    Get all watchlist items for a user with token details.

    Args:
        user_id: User identifier

    Returns:
        List of watchlist items with nested token data
    """
    result = supabase.table("watchlists")\
        .select("*, tokens(*)")\
        .eq("user_id", user_id)\
        .order("added_at", desc=True)\
        .execute()

    return result.data or []


@router.post("/{user_id}")
def add_to_watchlist(user_id: str, item: WatchlistAddRequest) -> dict:
    """
    Add a token to user's watchlist.

    Args:
        user_id: User identifier
        item: Watchlist add request with mint address

    Returns:
        Created watchlist item

    Raises:
        HTTPException: If token not found or already in watchlist
    """
    # Check if token exists
    token = supabase.table("tokens")\
        .select("mint_address")\
        .eq("mint_address", item.mint_address)\
        .single()\
        .execute()

    if not token.data:
        raise HTTPException(status_code=404, detail="Token not found")

    # Check if already in watchlist
    existing = supabase.table("watchlists")\
        .select("id")\
        .eq("user_id", user_id)\
        .eq("mint_address", item.mint_address)\
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Token already in watchlist")

    # Add to watchlist
    result = supabase.table("watchlists").insert({
        "user_id": user_id,
        "mint_address": item.mint_address,
        "notes": item.notes
    }).execute()

    return result.data[0] if result.data else {}


@router.delete("/{user_id}/{mint_address}")
def remove_from_watchlist(user_id: str, mint_address: str) -> dict:
    """
    Remove a token from user's watchlist.

    Args:
        user_id: User identifier
        mint_address: Token mint address to remove

    Returns:
        Status message

    Raises:
        HTTPException: If watchlist item not found
    """
    result = supabase.table("watchlists")\
        .delete()\
        .eq("user_id", user_id)\
        .eq("mint_address", mint_address)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    return {"status": "removed", "mint_address": mint_address}


@router.get("/{user_id}/check/{mint_address}")
def check_watchlist(user_id: str, mint_address: str) -> dict:
    """
    Check if a token is in user's watchlist.

    Args:
        user_id: User identifier
        mint_address: Token mint address to check

    Returns:
        Dict with in_watchlist boolean
    """
    result = supabase.table("watchlists")\
        .select("id")\
        .eq("user_id", user_id)\
        .eq("mint_address", mint_address)\
        .execute()

    return {"in_watchlist": bool(result.data)}


@router.patch("/{user_id}/{mint_address}")
def update_watchlist_notes(user_id: str, mint_address: str, notes: str) -> dict:
    """
    Update notes for a watchlist item.

    Args:
        user_id: User identifier
        mint_address: Token mint address
        notes: New notes text

    Returns:
        Updated watchlist item

    Raises:
        HTTPException: If watchlist item not found
    """
    result = supabase.table("watchlists")\
        .update({"notes": notes})\
        .eq("user_id", user_id)\
        .eq("mint_address", mint_address)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    return result.data[0]
