def compute_meme_score(
    posts_per_min: int,
    engagement: int,
    sentiment: float,
    uniqueness: str
):
    """
    Compute MemeScore (0–100)
    """

    # 1) Social Velocity
    if posts_per_min > 100:
        social_velocity_score = 25
    elif posts_per_min >= 50:
        social_velocity_score = 18
    elif posts_per_min >= 10:
        social_velocity_score = 10
    else:
        social_velocity_score = 5

    # 2) Engagement Score
    if engagement > 5000:
        engagement_score = 25
    elif engagement >= 2000:
        engagement_score = 18
    elif engagement >= 500:
        engagement_score = 10
    else:
        engagement_score = 5

    # 3) Sentiment Score
    if sentiment > 0.5:
        sentiment_score = 25
    elif sentiment >= 0.1:
        sentiment_score = 18
    elif sentiment >= -0.2:
        sentiment_score = 10
    else:
        sentiment_score = 5

    # 4) Meme Uniqueness Score
    uniqueness = uniqueness.lower()
    if uniqueness == "original":
        uniqueness_score = 25
    elif uniqueness == "derivative":
        uniqueness_score = 10
    else:
        uniqueness_score = 5

    total = (
        social_velocity_score
        + engagement_score
        + sentiment_score
        + uniqueness_score
    )

    return {
        "meme_score": total,
        "components": {
            "social_velocity_score": social_velocity_score,
            "engagement_score": engagement_score,
            "sentiment_score": sentiment_score,
            "uniqueness_score": uniqueness_score
        }
    }
