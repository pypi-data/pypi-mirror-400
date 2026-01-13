from enum import Enum


class GovernanceExpiryType(str, Enum):
    ABSOLUTE = "ABSOLUTE"
    NONE = "NONE"
    RELATIVE_COMPLETION = "RELATIVE_COMPLETION"
    RELATIVE_ENACTMENT = "RELATIVE_ENACTMENT"
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
