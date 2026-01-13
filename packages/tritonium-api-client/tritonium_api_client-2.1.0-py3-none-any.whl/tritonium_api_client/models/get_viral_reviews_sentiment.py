from enum import Enum

class GetViralReviewsSentiment(str, Enum):
    ALL = "all"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"

    def __str__(self) -> str:
        return str(self.value)
