from enum import Enum

class GetSubscriptionV2Response200SubscriptionBillingCycle(str, Enum):
    ANNUAL = "annual"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        return str(self.value)
