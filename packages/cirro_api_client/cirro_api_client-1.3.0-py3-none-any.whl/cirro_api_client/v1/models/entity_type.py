from enum import Enum


class EntityType(str, Enum):
    DATASET = "DATASET"
    DISCUSSION = "DISCUSSION"
    NOTEBOOK = "NOTEBOOK"
    PROCESS = "PROCESS"
    PROJECT = "PROJECT"
    REFERENCE = "REFERENCE"
    SAMPLE = "SAMPLE"
    SHARE = "SHARE"
    TAG = "TAG"
    UNKNOWN = "UNKNOWN"
    USER = "USER"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
