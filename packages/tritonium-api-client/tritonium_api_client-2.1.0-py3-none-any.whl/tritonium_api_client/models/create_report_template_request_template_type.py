from enum import Enum

class CreateReportTemplateRequestTemplateType(str, Enum):
    CUSTOM = "custom"
    EXECUTIVE_SUMMARY = "executive_summary"
    MONTHLY_STAKEHOLDER = "monthly_stakeholder"
    QUARTERLY_REVIEW = "quarterly_review"
    WEEKLY_TEAM = "weekly_team"

    def __str__(self) -> str:
        return str(self.value)
