from src.scores.dev_score import compute_dev_score
from src.scores.holder_score import compute_holder_score
from src.scores.risk_score import compute_risk_score
from src.scores.meme_score import compute_meme_score


def compute_final_score(
    # DevScore
    age_days,
    deployer_prior_count,
    rug_history,
    deployer_behavior,

    # HolderScore
    holder_count,
    whale_count,
    top10_pct,
    new_holder_growth,

    # RiskScore
    mint_auth_status,
    freeze_auth_status,
    liquidity_pct,
    dev_txn_count,

    # MemeScore
    posts_per_min,
    engagement,
    sentiment,
    uniqueness,
):
    dev = compute_dev_score(
        age_days,
        deployer_prior_count,
        rug_history,
        deployer_behavior,
    )["dev_score"]

    holders = compute_holder_score(
        holder_count,
        whale_count,
        top10_pct,
        new_holder_growth,
    )["holder_score"]

    risk = compute_risk_score(
        mint_auth_status,
        freeze_auth_status,
        liquidity_pct,
        dev_txn_count,
    )["risk_score"]

    meme = compute_meme_score(
        posts_per_min,
        engagement,
        sentiment,
        uniqueness,
    )["meme_score"]

    final = (
        dev * 0.30 +
        holders * 0.25 +
        risk * 0.25 +
        meme * 0.20
    )

    return {
        "final_score": round(final, 2),
        "components": {
            "dev_score": dev,
            "holder_score": holders,
            "risk_score": risk,
            "meme_score": meme,
        },
    }
