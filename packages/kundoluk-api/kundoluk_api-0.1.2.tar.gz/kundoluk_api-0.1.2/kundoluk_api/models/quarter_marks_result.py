from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Dict, Any

from ..utils.parsers import safe_get

if TYPE_CHECKING:
    from . import Teacher, QuarterMarks


@dataclass(frozen=True)
class QuarterMarksResult:
    """
    Модель элемента из actionResult эндпоинта qmarks/all
    
    Attributes:
        teacher: Основной учитель (часто null)
        quarter_marks: Список четвертных оценок
    """
    teacher: Optional[Teacher] = None
    quarter_marks: Optional[QuarterMarks] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["QuarterMarksResult"]:
        from . import Teacher, QuarterMarks

        if not data:
            return None
        
        teacher_data = safe_get(data, 'teacher', dict)
        teacher = Teacher.from_dict(teacher_data)
        
        quarter_marks_data = safe_get(data, 'quarterMarks', list)
        quarter_marks = QuarterMarks.from_dict(quarter_marks_data)
        
        return cls(
            teacher=teacher,
            quarter_marks=quarter_marks
        )
    
    def __repr__(self) -> str:
        count = len(self.quarter_marks.quarter_marks) if self.quarter_marks else 0
        return f"QuarterMarksResult(teacher={self.teacher!r}, marks_count={count})"

    def __str__(self) -> str:
        if not self.quarter_marks:
            return "Нет данных о четвертных оценках"
        
        return str(self.quarter_marks)