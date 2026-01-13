from enum import Enum

class MetricsDataType(str, Enum):
    EXTERNAL_FILE = "EXTERNAL_FILE"
    STANDARD = "STANDARD"
    VIDEO = "VIDEO"

    def __str__(self) -> str:
        return str(self.value)
