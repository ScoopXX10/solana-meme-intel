from src.utils.supabase_client import supabase
from src.scores.meme_combiner import compute_final_score


def _safe_get(data: dict, key: str, default):
    """Get value from dict, returning default if None or missing."""
    value = data.get(key)
    return value if value is not None else default


def score_token_in_db(mint_address: str):
    """Fetch token → compute score → store score."""
    result = supabase.table("tokens").select("*").eq("mint_address", mint_address).single().execute()

    if not result.data:
        print(f"[score] Token not found: {mint_address}")
        return None

    token = result.data

    # Compute the score with safe defaults for None values
    score = compute_final_score(
        _safe_get(token, "age_days", 30),
        _safe_get(token, "prior_tokens", {"total": 3, "successful": 2, "rugged": 1}),
        _safe_get(token, "rug_history", 0),
        _safe_get(token, "deployer_behavior", {"sol_in": 10, "sol_out": 5, "tx_count": 40}),

        _safe_get(token, "holder_count", 1000),
        _safe_get(token, "whale_count", 10),
        _safe_get(token, "top10_pct", 0.40),
        _safe_get(token, "new_growth", 0.10),

        _safe_get(token, "mint_auth", "renounced"),
        _safe_get(token, "freeze_auth", "renounced"),
        _safe_get(token, "liq_pct", 70),
        _safe_get(token, "dev_behavior", "normal"),

        _safe_get(token, "posts_per_min", 3),
        _safe_get(token, "engagement", 0.12),
        _safe_get(token, "sentiment", 0.55),
        _safe_get(token, "uniqueness", "original"),
    )

    # Store results
    supabase.table("tokens").update({
        "dev_score": score["components"]["dev_score"],
        "holder_score": score["components"]["holder_score"],
        "risk_score": score["components"]["risk_score"],
        "meme_score": score["components"]["meme_score"],
        "composite_score": score["final_score"],
    }).eq("mint_address", mint_address).execute()

    print(f"[score] Scored {mint_address}: {score['final_score']}")
    return score
