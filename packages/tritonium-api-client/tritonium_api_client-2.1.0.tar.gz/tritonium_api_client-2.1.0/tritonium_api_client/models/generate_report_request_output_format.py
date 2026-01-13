from enum import Enum

class GenerateReportRequestOutputFormat(str, Enum):
    HTML = "html"
    PDF = "pdf"
    PPTX = "pptx"

    def __str__(self) -> str:
        return str(self.value)
