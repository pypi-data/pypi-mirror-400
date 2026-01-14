from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Dict, Iterator, overload

if TYPE_CHECKING:
    from . import QuarterMarksResult, QuarterMarks


@dataclass(frozen=True)
class QuarterMarksResults:
    """
    Контейнер для списка QuarterMarksResult
    
    Attributes:
        results: Список объектов QuarterMarksResult
    """
    results: List[QuarterMarksResult]
    
    def __iter__(self) -> Iterator[QuarterMarksResult]:
        return iter(self.results)
    
    @overload
    def __getitem__(self, index: int) -> QuarterMarksResult: ...
    
    @overload
    def __getitem__(self, index: slice) -> List[QuarterMarksResult]: ...
    
    def __getitem__(self, index):
        return self.results[index]
    
    def __len__(self) -> int:
        return len(self.results)
    
    def __bool__(self) -> bool:
        return len(self.results) > 0
    
    @classmethod
    def from_dict(cls, data: List[Dict]) -> "QuarterMarksResults":
        from . import QuarterMarksResult
        
        if not data:
            return cls(results=[])
        
        results = [QuarterMarksResult.from_dict(item) for item in data if item]
        return cls(results=results)
    
    def get_all_quarter_marks(self) -> QuarterMarks:
        """
        Извлечь все QuarterMark из всех результатов
        
        Returns:
            QuarterMarks со всеми оценками
        """
        from . import QuarterMarks
        
        all_marks = []
        for result in self.results:
            if result and result.quarter_marks:
                all_marks.extend(result.quarter_marks.quarter_marks)
        
        return QuarterMarks(all_marks)
    
    def __repr__(self) -> str:
        results_str = ', '.join(repr(result) for result in self.results[:2])
        if len(self.results) > 2:
            results_str += f", ... (+{len(self.results)-2} результатов)"
        return f"QuarterMarksResults([{results_str}])"
    
    def __str__(self) -> str:
        if not self.results:
            return "Нет данных об оценках"
        
        all_marks = self.get_all_quarter_marks()
        
        if not all_marks.quarter_marks:
            return "Нет оценок"
        
        subject_grades = {}
        for mark in all_marks.quarter_marks:
            subject = mark.subject_name_ru or mark.subject_name_kg or "Неизвестный"
            if subject not in subject_grades:
                subject_grades[subject] = {}
            
            quarter = mark.quarter or 0
            if quarter not in subject_grades[subject]:
                subject_grades[subject][quarter] = []
            
            if mark.quarter_mark:
                subject_grades[subject][quarter].append(str(mark.quarter_mark))
            elif mark.custom_mark:
                subject_grades[subject][quarter].append(mark.custom_mark)
        
        lines = [f"Всего оценок: {len(all_marks.quarter_marks)}"]
        
        for subject, quarters in sorted(subject_grades.items()):
            quarter_strs = []
            for quarter in sorted(quarters.keys()):
                if quarter == 5:
                    quarter_name = "год"
                elif quarter == 0:
                    quarter_name = "без четв."
                else:
                    quarter_name = f"{quarter} четв."
                
                grades = ", ".join(quarters[quarter])
                quarter_strs.append(f"{quarter_name}: {grades}")
            
            lines.append(f"  {subject}: {'; '.join(quarter_strs)}")
        
        return "\n".join(lines)