from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from . import QuarterMark
    

@dataclass(frozen=True)
class QuarterMarks:
    """
    Контейнер для хранения списка четвертных оценок
    
    Attributes:
        quarter_marks: Список объектов QuarterMark
    """
    quarter_marks: List[QuarterMark]
    
    def __iter__(self):
        return iter(self.quarter_marks)
    
    def __len__(self) -> int:
        return len(self.quarter_marks)
    
    def __bool__(self) -> bool:
        return len(self.quarter_marks) > 0
    
    def __getitem__(self, index):
        return self.quarter_marks[index]
    
    @classmethod
    def from_dict(cls, data: List[Dict]) -> "QuarterMarks":
        from . import QuarterMark

        if not data:
            return cls(quarter_marks=[])
        
        quarter_marks = set()
        
        for item in data:
            if not item:
                continue
                
            mark = QuarterMark.from_dict(item)
            if mark:
                quarter_marks.add(mark)
        
        return cls(quarter_marks=list(quarter_marks))
    
    def __repr__(self) -> str:
        marks_str = ', '.join(repr(mark) for mark in self.quarter_marks[:3])
        if len(self.quarter_marks) > 3:
            marks_str += f", ... (+{len(self.quarter_marks)-3} оценок)"
        return f"QuarterMarks([{marks_str}])"

    def __str__(self) -> str:
        if not self.quarter_marks:
            return "Нет четвертных оценок"
        
        by_quarter = {}
        for mark in self.quarter_marks:
            quarter = mark.quarter or 0
            if quarter not in by_quarter:
                by_quarter[quarter] = []
            by_quarter[quarter].append(mark)
        
        lines = []
        
        quarter_order = [1, 2, 3, 4, 5] + [q for q in sorted(by_quarter.keys()) if q not in [1, 2, 3, 4, 5]]
        
        for quarter in quarter_order:
            if quarter not in by_quarter:
                continue
                
            if quarter == 5:
                quarter_name = "Годовая"
            elif quarter == 0:
                quarter_name = "Без четверти"
            else:
                quarter_name = f"{quarter} четверть"
            
            lines.append(f"\n{quarter_name}:")
            
            for mark in sorted(by_quarter[quarter], key=lambda m: m.subject_name_ru or m.subject_name_kg or ""):
                lines.append(f"  {mark}")
        
        return "\n".join(lines)