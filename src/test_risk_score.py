from scores.risk_score import compute_risk_score

result = compute_risk_score(
    mint_revoked=True,
    freeze_revoked=False,
    liquidity_pct=60,
    dev_behavior="normal"
)

print(result)
