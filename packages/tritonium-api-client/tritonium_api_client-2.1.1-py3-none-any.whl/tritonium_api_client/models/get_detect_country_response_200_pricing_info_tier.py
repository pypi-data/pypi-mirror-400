from enum import Enum

class GetDetectCountryResponse200PricingInfoTier(str, Enum):
    FULL = "FULL"
    TIER20 = "TIER20"
    TIER40 = "TIER40"
    TIER60 = "TIER60"

    def __str__(self) -> str:
        return str(self.value)
