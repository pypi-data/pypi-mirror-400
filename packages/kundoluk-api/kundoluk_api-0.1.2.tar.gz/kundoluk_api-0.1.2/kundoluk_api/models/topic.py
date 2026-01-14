from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

from ..utils.parsers import safe_get, parse_date


@dataclass(frozen=True)
class Topic:
    """
    Модель темы урока
    
    Attributes:
        code: Код темы (обычно 0)
        name: Название темы урока
        short: Краткое описание темы
        lesson_day: Дата, к которой привязана тема
    """
    code: Optional[int] = None
    name: Optional[str] = None
    short: Optional[str] = None
    lesson_day: Optional[date] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["Topic"]:
        if not data:
            return None
        
        lesson_day_str = safe_get(data, 'lessonDay', str)
        return cls(
            code=safe_get(data, 'code', int),
            name=safe_get(data, 'name', str),
            short=safe_get(data, 'short', str),
            lesson_day=parse_date(lesson_day_str) if lesson_day_str else None
        )
    
    def __repr__(self) -> str:
        return f"Topic(code={self.code!r}, name={self.name!r}, short={self.short!r}, lesson_day={self.lesson_day!r})"

    def __str__(self) -> str:
        day_str = self.lesson_day.strftime("%d.%m.%Y") if self.lesson_day else "Дата не указана"
        return f"Тема: {self.name or 'Нет названия'} ({day_str})"