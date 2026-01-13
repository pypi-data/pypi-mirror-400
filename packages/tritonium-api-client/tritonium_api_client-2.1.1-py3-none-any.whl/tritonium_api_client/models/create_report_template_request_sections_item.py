from enum import Enum

class CreateReportTemplateRequestSectionsItem(str, Enum):
    AI_RECOMMENDATIONS = "ai_recommendations"
    ALERT_SUMMARY = "alert_summary"
    COMPETITOR_MENTIONS = "competitor_mentions"
    FEATURE_REQUESTS = "feature_requests"
    GEOGRAPHIC_BREAKDOWN = "geographic_breakdown"
    RATING_DISTRIBUTION = "rating_distribution"
    RESPONSE_METRICS = "response_metrics"
    REVIEW_VOLUME_TRENDS = "review_volume_trends"
    SENTIMENT_OVERVIEW = "sentiment_overview"
    TESTIMONIALS = "testimonials"
    TOP_ISSUES = "top_issues"

    def __str__(self) -> str:
        return str(self.value)
