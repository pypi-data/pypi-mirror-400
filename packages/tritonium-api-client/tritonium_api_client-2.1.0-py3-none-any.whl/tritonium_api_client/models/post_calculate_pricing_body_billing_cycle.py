from enum import Enum

class PostCalculatePricingBodyBillingCycle(str, Enum):
    ANNUAL = "annual"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        return str(self.value)
