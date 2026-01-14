from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..utils.parsers import safe_get


@dataclass(frozen=True)
class Teacher:
    """
    Модель учителя
    
    Attributes:
        pin: Персональный идентификационный номер учителя (как число)
        first_name: Имя учителя
        last_name: Фамилия учителя
        mid_name: Отчество учителя
    """
    pin: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mid_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["Teacher"]:
        if not data:
            return None
        
        return cls(
            pin=safe_get(data, 'pin', int),
            first_name=safe_get(data, 'first_name', str),
            last_name=safe_get(data, 'last_name', str),
            mid_name=safe_get(data, 'mid_name', str)
        )
    
    def __repr__(self) -> str:
        return f"Teacher(pin={self.pin!r}, last_name={self.last_name!r})"

    def __str__(self) -> str:
        name_parts = [self.last_name, self.first_name]
        name = " ".join(filter(None, name_parts))
        return f"Учитель: {name or 'Неизвестно'}"

    def __hash__(self):
        return hash(self.pin)

    def __eq__(self, other):
        if not isinstance(other, Teacher):
            return False
        return self.pin == other.pin