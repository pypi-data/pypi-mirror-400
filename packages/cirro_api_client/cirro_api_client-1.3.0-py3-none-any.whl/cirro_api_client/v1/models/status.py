from enum import Enum


class Status(str, Enum):
    ARCHIVED = "ARCHIVED"
    COMPLETED = "COMPLETED"
    DELETE = "DELETE"
    DELETED = "DELETED"
    DELETING = "DELETING"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
