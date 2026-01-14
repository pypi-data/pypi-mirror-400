from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Dict, List, Any
from datetime import datetime

from ..utils.parsers import safe_get, parse_datetime

if TYPE_CHECKING:
    from . import Teacher


@dataclass(frozen=True)
class QuarterMark:
    """
    Модель четвертной/семестровой оценки
    
    Attributes:
        object_id: Уникальный ID записи об оценке
        grade_id: UUID класса/параллели ученика
        student_id: UUID ученика
        subject_id: UUID предмета
        
        quarter: Номер четверти (1-4, 5 - годовая)
        quarter_avg: Средний балл за четверть (может быть дробным)
        quarter_mark: Итоговая оценка за четверть (выставляется учителем)
        custom_mark: Специальная отметка (н/а, осв, зач и т.д.)
        is_bonus: Является ли оценка бонусной (за олимпиады, конкурсы)
        
        quarter_date: Дата и время выставления оценки
        subject_name_kg: Название предмета на кыргызском
        subject_name_ru: Название предмета на русском
        staff_id: ID преподавателя (часто null)
        
        teacher: Данные учителя, выставившего оценку
    """
    object_id: Optional[str] = None
    grade_id: Optional[str] = None
    student_id: Optional[str] = None
    subject_id: Optional[str] = None
    
    quarter: Optional[int] = None
    quarter_avg: Optional[float] = None
    quarter_mark: Optional[int] = None
    custom_mark: Optional[str] = None
    is_bonus: Optional[bool] = None
    
    quarter_date: Optional[datetime] = None
    subject_name_kg: Optional[str] = None
    subject_name_ru: Optional[str] = None
    staff_id: Optional[str] = None
    
    teacher: Optional[Teacher] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["QuarterMark"]:
        from . import Teacher

        if not data:
            return None
        
        quarter_num = safe_get(data, 'quarter', int)
        quarter_avg = safe_get(data, 'quarterAvg', (int, float))
        quarter_date = parse_datetime(safe_get(data, 'quarterDate', str))
        
        teacher_data = safe_get(data, 'teacher', dict)
        teacher = Teacher.from_dict(teacher_data)
        
        return cls(
            object_id=safe_get(data, 'objectId', str),
            grade_id=safe_get(data, 'gradeId', str),
            student_id=safe_get(data, 'studentId', str),
            subject_id=safe_get(data, 'subjectId', str),
            
            quarter=quarter_num,
            quarter_avg=quarter_avg,
            quarter_mark=safe_get(data, 'quarterMark', int),
            custom_mark=safe_get(data, 'customMark', str),
            is_bonus=safe_get(data, 'isBonus', bool),
            
            quarter_date=quarter_date,
            subject_name_kg=safe_get(data, 'subjectNameKg', str),
            subject_name_ru=safe_get(data, 'subjectNameRu', str),
            staff_id=safe_get(data, 'staffId', str),
            
            teacher=teacher
        )
    
    def __repr__(self) -> str:
        subject = self.subject_name_ru or self.subject_name_kg
        return f"QuarterMark(quarter={self.quarter!r}, subject={subject!r}, mark={self.quarter_mark!r})"

    def __str__(self) -> str:
        subject = self.subject_name_ru or self.subject_name_kg or "Предмет"
        quarter = f"{self.quarter} четверть" if self.quarter and self.quarter <= 4 else "Годовая"
        
        if self.custom_mark:
            mark = self.custom_mark 
        elif self.quarter_mark:
            mark = str(self.quarter_mark)
        else:
            mark = "?"
        
        parts = []
        if self.quarter_avg:
            parts.append(f"средний {self.quarter_avg}")
        if self.is_bonus:
            parts.append("бонус")
        if self.quarter_date:
            date_str = self.quarter_date.strftime("%d.%m")
            parts.append(f"от {date_str}")
        
        result = f"{subject}: {quarter} - {mark}"
        if parts:
            result += f" ({', '.join(parts)})"
        
        return result
    
    def __hash__(self):
        return hash(self.object_id)

    def __eq__(self, other):
        if not isinstance(other, QuarterMark):
            return False
        return self.object_id == other.object_id