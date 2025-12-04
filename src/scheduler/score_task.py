from src.utils.supabase_client import supabase
from src.scores.meme_combiner import compute_final_score

def score_token_in_db(mint_address: str):
    """Fetch token → compute score → store score."""
    result = supabase.table("tokens").select("*").eq("mint_address", mint_address).single().execute()

    if not result.data:
        print(f"[score] Token not found: {mint_address}")
        return None

    token = result.data

    # Compute the score
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
