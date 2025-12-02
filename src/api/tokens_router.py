from fastapi import APIRouter
from src.utils.supabase_client import supabase  # FIXED IMPORT

router = APIRouter(prefix="/tokens", tags=["tokens"])

@router.get("/")
def list_tokens():
    result = supabase.table("tokens").select("*").execute()
    return result.data

@router.get("/{mint_address}")
def get_token(mint_address: str):
    result = (
        supabase
        .table("tokens")
        .select("*")
        .eq("mint_address", mint_address)
        .single()
        .execute()
    )
    return result.data

@router.post("/refresh/{mint_address}")
def refresh_token(mint_address: str):
    # placeholder — will integrate Birdeye ingestion later
    from src.ingestion.update_token import update_single_token  # FIXED IMPORT
    update_single_token(mint_address)
    return {"status": "updated", "mint": mint_address}
