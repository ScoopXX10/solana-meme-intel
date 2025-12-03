from fastapi import APIRouter, HTTPException
from src.utils.supabase_client import supabase

from src.scores.dev_score import compute_dev_score
from src.scores.holder_score import compute_holder_score
from src.scores.risk_score import compute_risk_score
from src.scores.meme_score import compute_meme_score
from src.scores.meme_combiner import compute_final_score

router = APIRouter(prefix="/score", tags=["Score"])


@router.get("/{mint_address}")
def score_token(mint_address: str):
    # 1. Fetch token data from Supabase
    result = supabase.table("tokens").select("*").eq("mint_address", mint_address).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Token not found in database.")

    token = result.data

    # 2. Extract placeholder or stored fields
    # (Later these will come from RPC, Birdeye, etc.)
    dev_inputs = {
    "age_days": token.get("age_days", 30),

    "deployer_prior_count": token.get("prior_tokens", {
        "total": 3,
        "successful": 2,
        "rugged": 1
    }),

    "rug_history": token.get("rug_history", 0),

    "deployer_behavior": token.get("deployer_behavior", {
        "sol_in": 10,
        "sol_out": 5,
        "tx_count": 50
    }),
}


    holder_inputs = {
        "holder_count": token.get("holder_count", 1000),
        "whale_count": token.get("whale_count", 10),
        "top10_pct": token.get("top10_pct", 0.40),
        "new_holder_growth": token.get("new_growth", 0.10),
    }

    risk_inputs = {
    "mint_auth_status": token.get("mint_auth", "renounced"),
    "freeze_auth_status": token.get("freeze_auth", "renounced"),
    "liquidity_pct": token.get("liq_pct", 70),

    # If Supabase gives an integer, convert it into a meaningful string
    "dev_behavior": token.get("dev_behavior", "normal"),
    }


    meme_inputs = {
        "posts_per_min": token.get("posts_per_min", 3),
        "engagement": token.get("engagement", 0.12),
        "sentiment": token.get("sentiment", 0.55),
        "uniqueness": token.get("uniqueness", "original"),
    }

    # 3. Compute final score
    score = compute_final_score(
        dev_inputs["age_days"],
        dev_inputs["deployer_prior_count"],
        dev_inputs["rug_history"],
        dev_inputs["deployer_behavior"],

        holder_inputs["holder_count"],
        holder_inputs["whale_count"],
        holder_inputs["top10_pct"],
        holder_inputs["new_holder_growth"],

        risk_inputs["mint_auth_status"],
        risk_inputs["freeze_auth_status"],
        risk_inputs["liquidity_pct"],
        risk_inputs["dev_behavior"],

        meme_inputs["posts_per_min"],
        meme_inputs["engagement"],
        meme_inputs["sentiment"],
        meme_inputs["uniqueness"],
    )

    # 4. Save scores back into Supabase
    supabase.table("tokens").update({
    "dev_score": score["components"]["dev_score"],
    "holder_score": score["components"]["holder_score"],
    "risk_score": score["components"]["risk_score"],
    "meme_score": score["components"]["meme_score"],
    "composite_score": score["final_score"],  # <-- DB name
}).eq("mint_address", mint_address).execute()


    return {
        "mint": mint_address,
        "scores": score
    }
