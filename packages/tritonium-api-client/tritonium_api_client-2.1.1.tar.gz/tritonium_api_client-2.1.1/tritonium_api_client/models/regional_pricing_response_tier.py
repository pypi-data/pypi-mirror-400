from enum import Enum

class RegionalPricingResponseTier(str, Enum):
    FULL = "FULL"
    TIER20 = "TIER20"
    TIER40 = "TIER40"
    TIER60 = "TIER60"

    def __str__(self) -> str:
        return str(self.value)
