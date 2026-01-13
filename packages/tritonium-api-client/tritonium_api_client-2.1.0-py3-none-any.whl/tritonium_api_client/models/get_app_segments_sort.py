from enum import Enum

class GetAppSegmentsSort(str, Enum):
    REVIEW_COUNT = "review_count"
    SCORE = "score"
    SENTIMENT = "sentiment"

    def __str__(self) -> str:
        return str(self.value)
