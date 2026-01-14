"""
Token scoring task - computes scores based on real on-chain data.
"""
import logging
from src.utils.supabase_client import supabase
from src.scores.meme_combiner import compute_final_score

logger = logging.getLogger(__name__)


def _safe_get(data: dict, key: str, default):
    """Get value from dict, returning default if None or missing."""
    value = data.get(key)
    return value if value is not None else default


def score_token_in_db(mint_address: str):
    """
    Fetch token data from DB, compute score using real data, and store results.

    The scoring now uses real on-chain data when available:
    - mint_auth / freeze_auth: Real authority status from Helius
    - holder_count: Real holder count from on-chain data
    - top10_pct: Real top 10 holder concentration
    - whale_count: Real whale count (holders > 1% of supply)

    Defaults are used only when real data is not available.
    """
    result = supabase.table("tokens").select("*").eq("mint_address", mint_address).single().execute()

    if not result.data:
        logger.warning(f"Token not found: {mint_address}")
        return None

    token = result.data
    symbol = token.get("symbol", "???")

    # --- Dev Score inputs ---
    # These still use defaults as we don't have deployer wallet analysis yet
    age_days = _safe_get(token, "age_days", 30)
    prior_tokens = _safe_get(token, "prior_tokens", {"total": 0, "successful": 0, "rugged": 0})
    rug_history = _safe_get(token, "rug_history", 0)
    deployer_behavior = _safe_get(token, "deployer_behavior", {"sol_in": 0, "sol_out": 0, "tx_count": 0})

    # --- Holder Score inputs (NOW USES REAL DATA) ---
    holder_count = _safe_get(token, "holder_count", 100)  # Default low if unknown
    whale_count = _safe_get(token, "whale_count", 5)

    # top10_pct from DB is 0-100, holder_score expects 0-100 for top_holder_pct
    # We'll use top10_pct as a proxy for concentration
    top10_pct = _safe_get(token, "top10_pct", 50.0)

    # For gini and new_growth, we use estimates based on top10_pct
    # Higher concentration = higher gini (worse distribution)
    estimated_gini = min(1.0, top10_pct / 100 * 1.2) if top10_pct else 0.5
    new_growth = _safe_get(token, "new_growth", 10.0)  # Default conservative

    # --- Risk Score inputs (NOW USES REAL DATA) ---
    mint_auth = _safe_get(token, "mint_auth", "unknown")
    freeze_auth = _safe_get(token, "freeze_auth", "unknown")

    # Estimate LP percentage based on liquidity vs typical patterns
    # This is a rough estimate - ideally we'd check LP token locks
    liq_pct = _safe_get(token, "liq_pct", 50)  # Default middle ground

    # Dev behavior for risk score
    dev_behavior = _safe_get(token, "dev_behavior", "unknown")

    # --- Meme Score inputs ---
    # These still use defaults as we don't have social data integration yet
    posts_per_min = _safe_get(token, "posts_per_min", 1)
    engagement = _safe_get(token, "engagement", 100)
    sentiment = _safe_get(token, "sentiment", 0.3)
    uniqueness = _safe_get(token, "uniqueness", "derivative")

    # Compute the score
    score = compute_final_score(
        # Dev Score params
        age_days,
        prior_tokens,
        rug_history,
        deployer_behavior,

        # Holder Score params (REAL DATA)
        holder_count,
        whale_count,
        top10_pct,  # Used as top_holder_pct
        new_growth,

        # Risk Score params (REAL DATA)
        mint_auth,
        freeze_auth,
        liq_pct,
        dev_behavior,

        # Meme Score params
        posts_per_min,
        engagement,
        sentiment,
        uniqueness,
    )

    # Store results
    supabase.table("tokens").update({
        "dev_score": score["components"]["dev_score"],
        "holder_score": score["components"]["holder_score"],
        "risk_score": score["components"]["risk_score"],
        "meme_score": score["components"]["meme_score"],
        "composite_score": score["final_score"],
    }).eq("mint_address", mint_address).execute()

    logger.info(
        f"Scored {symbol} ({mint_address[:8]}...): "
        f"composite={score['final_score']:.1f} "
        f"[dev={score['components']['dev_score']}, "
        f"holder={score['components']['holder_score']}, "
        f"risk={score['components']['risk_score']}, "
        f"meme={score['components']['meme_score']}]"
    )

    return score


def score_all_tokens():
    """Score all tokens in the database."""
    result = supabase.table("tokens").select("mint_address, symbol").execute()
    tokens = result.data or []

    logger.info(f"Scoring {len(tokens)} tokens...")

    scored = 0
    for token in tokens:
        try:
            score_token_in_db(token["mint_address"])
            scored += 1
        except Exception as e:
            logger.error(f"Failed to score {token.get('symbol', '???')}: {e}")

    logger.info(f"Scored {scored}/{len(tokens)} tokens")
    return scored
