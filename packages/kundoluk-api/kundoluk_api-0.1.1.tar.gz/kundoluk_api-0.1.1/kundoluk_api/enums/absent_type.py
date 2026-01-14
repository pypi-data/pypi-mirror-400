from enum import Enum
import warnings

from ..kundoluk_warnings import EnumMissingWarning


class AbsentType(Enum):
    """
    Типы посещаемости
    
    Attributes:
        ABSENT = "absent"       # Отсутствовал
        LATE = "late"           # Опоздал
        PRESENT = "present"     # Присутствовал
    """
    ABSENT = "absent"
    LATE = "late"
    PRESENT = "present"

    EMPTY = ""
    
    @classmethod
    def _missing_(cls, value):
        if value:
            warnings.warn(EnumMissingWarning(cls, value), stacklevel=2)
        return cls.EMPTY