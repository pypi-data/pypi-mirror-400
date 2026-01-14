from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Optional, Union, List, Dict, Iterator, overload
from datetime import date
import warnings

from ..kundoluk_warnings import LessonParseWarning
from ..utils.parsers import parse_date

if TYPE_CHECKING:
    from . import DailySchedule


@dataclass(frozen=True)
class DailySchedules:
    """
    Контейнер для хранения списка дней/расписаний
    
    Attributes:
        daily_schedules: Список объектов DailySchedule
    """
    daily_schedules: List[DailySchedule]
    
    def __iter__(self) -> Iterator[DailySchedule]:
        return iter(self.daily_schedules)
    
    @overload
    def __getitem__(self, index: int) -> DailySchedule: ...
    @overload
    def __getitem__(self, index: slice) -> List[DailySchedule]: ...

    def __getitem__(self, index) -> DailySchedule:
        return self.daily_schedules[index]
    
    def __len__(self) -> int:
        return len(self.daily_schedules)
    
    def __bool__(self) -> bool:
        return len(self.daily_schedules) > 0
    
    def get_by_date(self, target_date: Union[date, str]) -> Optional[DailySchedule]:
        """Ищет расписание на конкретную дату"""
        target_date = parse_date(target_date)
        return next((ds for ds in self.daily_schedules if ds.date == target_date), None)

    def merge_quarter_marks(self, extra_schedules: List[DailySchedules]) -> DailySchedules:
        from . import Marks

        all_marks_map = {}
        for container in extra_schedules:
            if not container: continue
            
            for day in container:
                for lesson in day.lessons:
                    if not lesson.marks: continue

                    for mark in lesson.marks.marks:
                        all_marks_map[mark.uid] = mark

        marks_by_lesson = {}
        for mark in all_marks_map.values():
            if mark.ls_uid not in marks_by_lesson:
                marks_by_lesson[mark.ls_uid] = []
            marks_by_lesson[mark.ls_uid].append(mark)

        updated_days = []
        for day in self.daily_schedules:
            new_lessons = []
            for lesson in day.lessons:
                lesson_marks = marks_by_lesson.get(lesson.uid, [])
                if lesson_marks:
                    new_lesson = replace(lesson, marks=Marks(marks=lesson_marks))
                    new_lessons.append(new_lesson)
                else:
                    new_lessons.append(lesson)
            
            updated_days.append(replace(day, lessons=new_lessons))

        return replace(self, daily_schedules=updated_days)

    @classmethod
    def from_dict(cls, data: List[Dict]) -> DailySchedules:
        from . import Lesson, DailySchedule

        if not data:
            return cls(daily_schedules=[])

        lessons_by_date = {}
        
        for lesson_data in data:
            try:
                lesson = Lesson.from_dict(lesson_data)
                lesson_date = lesson.lesson_day.date()
                
                if lesson_date not in lessons_by_date:
                    lessons_by_date[lesson_date] = []
                
                lessons_by_date[lesson_date].append(lesson)
                
            except Exception as e:
                warnings.warn(
                    f"Ошибка при обработке урока {lesson_data.get('subject', 'unknown')}: {e}",
                    LessonParseWarning
                )
                continue
        
        daily_schedules = []
        for schedule_date, lessons in lessons_by_date.items():
            daily_schedule = DailySchedule(date=schedule_date, lessons=lessons)
            daily_schedule.sort_lessons()
            daily_schedules.append(daily_schedule)
        
        daily_schedules.sort(key=lambda x: x.date)
        
        return cls(daily_schedules=daily_schedules)
    
    def __repr__(self) -> str:
        count = len(self.daily_schedules)
        preview = ', '.join(repr(ds) for ds in self.daily_schedules[:2])
        suffix = f", ... (+{count-2})" if count > 2 else ""
        return f"DailySchedules([{preview}{suffix}])"
    
    def __str__(self) -> str:
        if not self.daily_schedules:
            return "Расписание пусто"
        
        total_days = len(self.daily_schedules)
        
        first_date = self.daily_schedules[0].date
        last_date = self.daily_schedules[-1].date
        
        if total_days == 1:
            return f"Расписание на {first_date}"
            
        return f"Расписание с {first_date} по {last_date} ({total_days} дней)"