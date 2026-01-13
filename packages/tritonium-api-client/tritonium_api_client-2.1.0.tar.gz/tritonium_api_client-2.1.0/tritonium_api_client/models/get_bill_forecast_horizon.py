from enum import Enum

class GetBillForecastHorizon(str, Enum):
    VALUE_0 = "7d"
    VALUE_1 = "30d"
    VALUE_2 = "90d"

    def __str__(self) -> str:
        return str(self.value)
