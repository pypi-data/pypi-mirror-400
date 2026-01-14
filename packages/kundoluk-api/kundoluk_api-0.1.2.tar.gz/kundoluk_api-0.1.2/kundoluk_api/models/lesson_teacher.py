from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Dict, Any

from ..utils.parsers import safe_get

if TYPE_CHECKING:
    from . import Marks


@dataclass(frozen=True)
class LessonTeacher:
    """
    Модель учителя в контексте урока
    
    Attributes:
        pin: Персональный идентификационный номер учителя (как число)
        pin_as_string: PIN как строка (14 цифр)
        first_name: Имя учителя
        last_name: Фамилия учителя
        mid_name: Отчество учителя
        marks: Оценки, выставленные учителем (обычно null в этом контексте)
    """
    pin: Optional[int] = None
    pin_as_string: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mid_name: Optional[str] = None
    marks: Optional[Marks] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["LessonTeacher"]:
        from . import Marks

        if not data:
            return None
        
        marks_data = safe_get(data, 'marks', list)
        marks = Marks.from_dict(marks_data)
        
        return cls(
            pin=safe_get(data, 'pin', int),
            pin_as_string=safe_get(data, 'pinAsString', str),
            first_name=safe_get(data, 'firstName', str),
            last_name=safe_get(data, 'lastName', str),
            mid_name=safe_get(data, 'midName', str),
            marks=marks
        )
    
    def __repr__(self) -> str:
        return f"LessonTeacher(pin={self.pin!r}, first_name={self.first_name!r}, last_name={self.last_name!r})"

    def __str__(self) -> str:
        name_parts = [self.last_name, self.first_name, self.mid_name]
        name = " ".join(filter(None, name_parts))
        return f"Учитель: {name or 'Неизвестно'}"
    
    def __hash__(self):
        return hash(self.pin)

    def __eq__(self, other):
        if not isinstance(other, LessonTeacher):
            return False
        return self.pin == other.pin