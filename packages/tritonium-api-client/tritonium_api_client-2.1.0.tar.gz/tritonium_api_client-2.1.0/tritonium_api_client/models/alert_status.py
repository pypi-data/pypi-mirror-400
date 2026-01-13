from enum import Enum

class AlertStatus(str, Enum):
    ACKNOWLEDGED = "acknowledged"
    READ = "read"
    SNOOZED = "snoozed"
    UNREAD = "unread"

    def __str__(self) -> str:
        return str(self.value)
