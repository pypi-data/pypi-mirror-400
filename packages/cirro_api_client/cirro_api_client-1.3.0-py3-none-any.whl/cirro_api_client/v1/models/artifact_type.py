from enum import Enum


class ArtifactType(str, Enum):
    FILES = "FILES"
    INGEST_MANIFEST = "INGEST_MANIFEST"
    METADATA = "METADATA"
    SAMPLE_SHEET = "SAMPLE_SHEET"
    WORKFLOW_COMPUTE_CONFIG = "WORKFLOW_COMPUTE_CONFIG"
    WORKFLOW_DAG = "WORKFLOW_DAG"
    WORKFLOW_DEBUG_LOGS = "WORKFLOW_DEBUG_LOGS"
    WORKFLOW_LOGS = "WORKFLOW_LOGS"
    WORKFLOW_OPTIONS = "WORKFLOW_OPTIONS"
    WORKFLOW_PARAMETERS = "WORKFLOW_PARAMETERS"
    WORKFLOW_REPORT = "WORKFLOW_REPORT"
    WORKFLOW_TIMELINE = "WORKFLOW_TIMELINE"
    WORKFLOW_TRACE = "WORKFLOW_TRACE"
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
