# src/scores/dev_score.py

def compute_dev_score(age_days, prior_tokens, rug_history, behavior) -> dict:
    """
    Returns dev score (0-100) and component breakdown.
    """

    # ===== Wallet Age Score =====
    wallet_age = age_days

    if wallet_age >= 120:
        age_score = 25
    elif wallet_age >= 60:
        age_score = 20
    elif wallet_age >= 30:
        age_score = 15
    else:
        age_score = 5

    # ===== Prior Token Score =====
    prior = prior_tokens

    if prior["total"] == 0:
        prior_score = 10
    else:
        success_rate = prior["successful"] / prior["total"]
        prior_score = int(success_rate * 25)

    # ===== Rug History =====
    rug_penalty = prior["rugged"] * 10
    rug_score = max(0, 20 - rug_penalty)

    # ===== Behavior Score =====
    if isinstance(behavior, dict):
        tx_count = behavior.get("tx_count", 0)
    else:
        tx_count = 0

    if tx_count > 200:
        behavior_score = 20
    elif tx_count > 50:
        behavior_score = 15
    elif tx_count > 10:
        behavior_score = 10
    else:
        behavior_score = 5

    # ===== Combined =====
    total = age_score + prior_score + rug_score + behavior_score

    return {
        "dev_score": min(total, 100),
        "components": {
            "age_score": age_score,
            "prior_score": prior_score,
            "rug_score": rug_score,
            "behavior_score": behavior_score,
        },
    }
