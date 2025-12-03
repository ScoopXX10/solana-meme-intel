# src/scores/risk_score.py

def compute_risk_score(
    mint_auth_status: str,
    freeze_auth_status: str,
    liquidity_pct: float,
    dev_behavior,
) -> dict:
    """
    Returns a risk_score between 0 and 100 where HIGHER = SAFER.

    Inputs:
      - mint_auth_status: e.g. "renounced", "single-sig", "multi-sig"
      - freeze_auth_status: same idea
      - liquidity_pct: % of supply in LP (0–100)
      - dev_behavior: can be a string ("normal", "aggressive", etc.)
                      OR a number (e.g. tx count)
    """

    # ---------- Mint authority ----------
    mint = (mint_auth_status or "").lower()
    if mint in ("renounced", "none", ""):
        mint_score = 25
    elif mint in ("multi-sig", "multisig"):
        mint_score = 18
    else:
        mint_score = 10  # single-sig / unknown

    # ---------- Freeze authority ----------
    freeze = (freeze_auth_status or "").lower()
    if freeze in ("renounced", "none", ""):
        freeze_score = 25
    elif freeze in ("multi-sig", "multisig"):
        freeze_score = 18
    else:
        freeze_score = 8

    # ---------- Liquidity ----------
    try:
        lp = float(liquidity_pct)
    except (TypeError, ValueError):
        lp = 0.0

    lp = max(0.0, min(lp, 100.0))

    if lp >= 80:
        liq_score = 25
    elif lp >= 50:
        liq_score = 18
    elif lp >= 25:
        liq_score = 12
    else:
        liq_score = 5

    # ---------- Dev behavior ----------
    # Accepts either a string label OR a numeric proxy
    if isinstance(dev_behavior, str):
        behavior = dev_behavior.lower()
    elif isinstance(dev_behavior, (int, float)):
        # Treat as "activity intensity" (e.g., tx count)
        if dev_behavior > 200:
            behavior = "aggressive"
        elif dev_behavior > 50:
            behavior = "active"
        else:
            behavior = "low"
    else:
        behavior = "unknown"

    if behavior in ("low", "normal"):
        dev_score = 25
    elif behavior in ("active", "medium"):
        dev_score = 18
    elif behavior in ("aggressive", "suspicious"):
        dev_score = 10
    else:
        dev_score = 15

    total = mint_score + freeze_score + liq_score + dev_score
    total = max(0, min(total, 100))

    return {
        "risk_score": total,
        "components": {
            "mint_score": mint_score,
            "freeze_score": freeze_score,
            "liq_score": liq_score,
            "dev_behavior_score": dev_score,
        },
    }

