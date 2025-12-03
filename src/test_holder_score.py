from scores.holder_score import compute_holder_score

result = compute_holder_score(
    holder_count=2000,
    top_holder_pct=18,
    gini=0.42,
    new_holder_growth=35
)

print(result)
