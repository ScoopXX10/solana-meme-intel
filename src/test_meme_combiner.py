from scores.meme_combiner import compute_final_score

result = compute_final_score(
    # DevScore inputs
    age_days=45,
    prior_tokens={
        "total": 5,
        "successful": 4,
        "rugged": 1
    },
    rug_history=1,
    deployer_behavior={
        "sol_in": 12,
        "sol_out": 9,
        "tx_count": 45
    },

    # Onchain Score inputs
    txn_count_1h=320,
    volume_1h=1200,
    holder_growth=0.25,
    liquidity=80000,

    # Social Score inputs
    followers=1500,
    engagement_rate=0.12,
    sentiment=0.65,

    # Meme Score
    uniqueness="original",
)

print(
    compute_final_score(
        age_days=45,
        prior_tokens={"total":5, "successful":4, "rugged":1},
        rug_history=1,
        deployer_behavior={"sol_in":12, "sol_out":9, "tx_count":45},
        txn_count_1h=0,
        volume_1h=0,
        holder_growth=0,
        liquidity=0,
        followers=0,
        engagement_rate=0,
        sentiment=0,
        uniqueness="meh",
    )
)

