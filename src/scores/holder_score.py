def compute_holder_score(
    holder_count: int,
    top_holder_pct: float,
    gini: float,
    new_holder_growth: float
):
    """
    Compute HolderScore out of 100.

    Inputs:
        holder_count        - total number of unique holders
        top_holder_pct      - % supply held by top 1 wallet (0–100)
        gini                - inequality score (0–1)
        new_holder_growth   - % growth in new holders recently (0–100)
    """

    # 1) Holder Count Score (0–30)
    if holder_count >= 5000:
        holder_count_score = 30
    elif holder_count >= 1000:
        holder_count_score = 20
    elif holder_count >= 250:
        holder_count_score = 10
    else:
        holder_count_score = 5

    # 2) Whale Score (0–30)
    # Ranking is flipped — lower top_holder_pct = better
    if top_holder_pct <= 10:
        whale_score = 30
    elif top_holder_pct <= 25:
        whale_score = 20
    elif top_holder_pct <= 50:
        whale_score = 10
    else:
        whale_score = 5

    # 3) Distribution Score (0–20)
    # Lower gini = better distribution
    if gini <= 0.3:
        distribution_score = 20
    elif gini <= 0.5:
        distribution_score = 10
    else:
        distribution_score = 5

    # 4) New Holder Growth (0–20)
    if new_holder_growth >= 50:
        new_holder_score = 20
    elif new_holder_growth >= 20:
        new_holder_score = 10
    else:
        new_holder_score = 5

    total = (
        holder_count_score
        + whale_score
        + distribution_score
        + new_holder_score
    )

    return {
        "holder_score": total,
        "components": {
            "holder_count_score": holder_count_score,
            "whale_score": whale_score,
            "distribution_score": distribution_score,
            "new_holder_score": new_holder_score,
        },
    }
