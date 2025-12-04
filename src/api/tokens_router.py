from fastapi import APIRouter, HTTPException
from src.utils.supabase_client import supabase
from src.ingestion.update_token import update_single_token
from src.scores.meme_combiner import compute_final_score

router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.get("/")
def list_tokens():
    result = supabase.table("tokens").select("*").execute()
    return result.data


@router.get("/{mint_address}")
def get_token(mint_address: str):
    result = (
        supabase.table("tokens")
        .select("*")
        .eq("mint_address", mint_address)
        .single()
        .execute()
    )
    return result.data


@router.post("/refresh/{mint_address}")
def refresh_token(mint_address: str):

    # 1. Attempt to update via Birdeye
    success = update_single_token(mint_address)

    # Do NOT raise 404 just because Birdeye is down
    if not success:
        # Continue anyway — scoring still works using existing DB data
        print("Birdeye returned no data; continuing with stored values.")

    # 2. Load updated token from DB
    result = (
        supabase.table("tokens")
        .select("*")
        .eq("mint_address", mint_address)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(500, "Token not found after refresh attempt")

    token = result.data

    # 3. Compute fresh score
    score = compute_final_score(
        token.get("age_days", 30),
        token.get("prior_tokens", {"total": 3, "successful": 2, "rugged": 1}),
        token.get("rug_history", 0),
        token.get("deployer_behavior", {"sol_in": 10, "sol_out": 5, "tx_count": 40}),

        token.get("holder_count", 1000),
        token.get("whale_count", 10),
        token.get("top10_pct", 0.40),
        token.get("new_growth", 0.10),

        token.get("mint_auth", "renounced"),
        token.get("freeze_auth", "renounced"),
        token.get("liq_pct", 70),
        token.get("dev_behavior", "normal"),

        token.get("posts_per_min", 3),
        token.get("engagement", 0.12),
        token.get("sentiment", 0.55),
        token.get("uniqueness", "original"),
    )

    # 4. Save scores into DB under composite_score
    supabase.table("tokens").update({
        "dev_score": score["components"]["dev_score"],
        "holder_score": score["components"]["holder_score"],
        "risk_score": score["components"]["risk_score"],
        "meme_score": score["components"]["meme_score"],
        "composite_score": score["final_score"]
    }).eq("mint_address", mint_address).execute()

    # 5. Return payload
    return {
        "status": "refresh_complete",
        "mint": mint_address,
        "token": token,
        "scores": score
    }
@router.get("/scored")
def list_scored_tokens():
    result = (
        supabase.table("tokens")
        .select("mint_address, symbol, name, price, composite_score")
        .order("composite_score", desc=True)
        .execute()
    )

    return result.data