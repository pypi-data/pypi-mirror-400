from enum import Enum

class ConflatedBatchStatus(str, Enum):
    BLOCKER = "BLOCKER"
    CANCELLED = "CANCELLED"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    RUNNING = "RUNNING"
    SUBMITTED = "SUBMITTED"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
