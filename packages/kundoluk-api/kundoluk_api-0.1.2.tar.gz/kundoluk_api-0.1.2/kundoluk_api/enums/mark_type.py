from enum import Enum
import warnings

from ..kundoluk_warnings import EnumMissingWarning


class MarkType(Enum):
    """
    Типы оценок

    Attributes:
        GENERAL = "general"       # Обычная оценка
        CONTROL = "control"       # Контрольная работа
        HOMEWORK = "homework"     # Домашняя работа
        TEST = "test"             # Тест
        LABORATORY = "laboratory" # Лабораторная
        WRITE = "write"           # Письменная
        PRACTICE = "practice"     # Практическая
    """
    GENERAL = "general"
    CONTROL = "control"
    HOMEWORK = "homework"

    LABORATORY = "laboratory"
    WRITE = "write"
    PRACTICE = "practice"

    TEST = "test"

    EMPTY = ""
    
    @classmethod
    def _missing_(cls, value):
        if value:
            warnings.warn(EnumMissingWarning(cls, value), stacklevel=2)
        return cls.EMPTY