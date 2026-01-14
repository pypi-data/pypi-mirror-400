from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Iterator, overload

if TYPE_CHECKING:
    from . import Mark


@dataclass(frozen=True)
class Marks:
    """
    Контейнер для хранения списка оценок
    
    Attributes:
        marks: Список объектов Mark
    """
    marks: List[Mark]
    
    def __iter__(self) -> Iterator[Mark]:
        return iter(self.marks)
    
    @overload
    def __getitem__(self, index: int) -> Mark: ...
    @overload
    def __getitem__(self, index: slice) -> List[Mark]: ...

    def __getitem__(self, index) -> Mark:
        return self.marks[index]
    
    def __len__(self) -> int:
        return len(self.marks)
    
    def __bool__(self) -> bool:
        return len(self.marks) > 0
    
    @classmethod
    def from_dict(cls, data: List) -> Marks:
        from . import Mark

        if not data:
            return cls(marks=[])
        
        marks = [Mark.from_dict(mark_data) for mark_data in data]
        return cls(marks=marks)
    
    def __repr__(self) -> str:
        marks_str = ', '.join(repr(mark) for mark in self.marks[:3])
        if len(self.marks) > 3:
            marks_str += f", ... (+{len(self.marks)-3} оценок)"
        return f"Marks([{marks_str}])"

    def __str__(self) -> str:
        if not self.marks:
            return "Оценки: нет оценок"
        marks_list = []
        for mark in self.marks[:5]:
            if mark.value:
                marks_list.append(str(mark.value))
            elif mark.custom_mark:
                marks_list.append(mark.custom_mark)
            elif mark.is_absent:
                marks_list.append("Н")
            else:
                marks_list.append("?")
        
        result = f"Оценки: {', '.join(marks_list)}"
        if len(self.marks) > 5:
            result += f" (всего {len(self.marks)} оценок)"
        return result