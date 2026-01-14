from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

from ..utils.parsers import safe_get, parse_date


@dataclass(frozen=True)
class Task:
    """
    Модель учебного задания (домашнего задания)
    
    Attributes:
        code: Код задания (обычно 0)
        name: Текст задания
        note: Дополнительные примечания к заданию
        lesson_day: Дата, к которой привязано задание
    """
    code: Optional[int] = None
    name: Optional[str] = None
    note: Optional[str] = None
    lesson_day: Optional[date] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["Task"]:
        if not data:
            return None
        
        lesson_day_str = safe_get(data, 'lessonDay', str)
        return cls(
            code=safe_get(data, 'code', int),
            name=safe_get(data, 'name', str),
            note=safe_get(data, 'note', str),
            lesson_day=parse_date(lesson_day_str) if lesson_day_str else None
        )
    
    def __repr__(self) -> str:
        return f"Task(code={self.code!r}, name={self.name!r}, lesson_day={self.lesson_day!r})"

    def __str__(self) -> str:
        day_str = self.lesson_day.strftime("%d.%m.%Y") if self.lesson_day else "Дата не указана"
        task_preview = (self.name[:50] + "...") if self.name and len(self.name) > 50 else self.name
        return f"Задание: {task_preview or 'Нет задания'} ({day_str})"