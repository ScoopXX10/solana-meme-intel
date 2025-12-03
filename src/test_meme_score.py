from scores.meme_score import compute_meme_score

result = compute_meme_score(
    posts_per_min=120,
    engagement=6000,
    sentiment=0.7,
    uniqueness="original"
)

print(result)
