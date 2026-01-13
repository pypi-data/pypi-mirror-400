from enum import Enum


class GovernanceAccessType(str, Enum):
    FULFILLMENT_DOWNLOAD = "FULFILLMENT_DOWNLOAD"
    FULFILLMENT_UPLOAD = "FULFILLMENT_UPLOAD"
    GOVERNANCE_DOWNLOAD = "GOVERNANCE_DOWNLOAD"
    GOVERNANCE_UPLOAD = "GOVERNANCE_UPLOAD"
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
