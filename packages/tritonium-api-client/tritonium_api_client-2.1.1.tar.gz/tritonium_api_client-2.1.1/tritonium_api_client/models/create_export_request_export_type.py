from enum import Enum

class CreateExportRequestExportType(str, Enum):
    ALERTS = "alerts"
    ANALYTICS = "analytics"
    INSIGHTS = "insights"
    REPLIES = "replies"
    REVIEWS = "reviews"

    def __str__(self) -> str:
        return str(self.value)
