from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from typing import TYPE_CHECKING, List, Optional, overload

if TYPE_CHECKING:
    from . import Lesson, DailySchedules


@dataclass(frozen=True)
class DailySchedule:
    """
    Ежедневное расписание уроков
    
    Attributes:
        date: Дата расписания
        lessons: Список уроков на этот день
    """
    lessons: List[Lesson]
    date: date = None
    
    def sort_lessons(self) -> None:
        """Сортирует уроки по номеру урока (lesson_number)"""
        self.lessons.sort(key=lambda x: x.lesson_number)
    
    def get_lessons_by_teacher(self, teacher_name: str) -> List[Lesson]:
        """Возвращает уроки с указанным учителем"""
        return [lesson for lesson in self.lessons 
                if lesson.teacher and 
                (teacher_name.lower() == lesson.teacher.last_name.lower() or
                 teacher_name.lower() == lesson.teacher.first_name.lower() or
                 teacher_name.lower() == lesson.teacher.mid_name.lower())]
    
    def get_lessons_by_subject(self, subject_name: str) -> List[Lesson]:
        """Возвращает уроки по указанному предмету"""
        return [lesson for lesson in self.lessons 
                if lesson.subject and 
                subject_name.lower() == str(lesson.subject).lower()]
    
    def get_lesson_at_time(self, time_str: str) -> Optional[Lesson]:
        """Возвращает урок в указанное время"""
        for lesson in self.lessons:
            if lesson.start_time == time_str:
                return lesson
        return None
    
    def merge_extra_mark_data(self, schedule_list: List[DailySchedule]) -> DailySchedule:
        from . import Marks

        all_unique_marks = {}

        for schedule in schedule_list:
            if not schedule: continue

            for lesson in schedule:
                if not lesson.marks: continue
                for mark in lesson.marks.marks:
                    all_unique_marks[mark.uid] = mark

        marks_by_lesson = {}
        for mark in all_unique_marks.values():
            if mark.ls_uid not in marks_by_lesson:
                marks_by_lesson[mark.ls_uid] = []
            marks_by_lesson[mark.ls_uid].append(mark)

        new_lessons = []
        for lesson in self.lessons:
            lesson_marks = marks_by_lesson.get(lesson.uid, [])
            
            if lesson_marks:
                new_marks_obj = Marks(marks=lesson_marks)
                new_lessons.append(replace(lesson, marks=new_marks_obj))
            else:
                new_lessons.append(lesson)

        return replace(self, lessons=new_lessons)

    @overload
    def __getitem__(self, index: int) -> Lesson: ...
    @overload
    def __getitem__(self, index: slice) -> List[Lesson]: ...

    def __getitem__(self, index) -> Lesson:
        return self.lessons[index]
    
    def __len__(self) -> int:
        return len(self.lessons)
    
    def __bool__(self) -> bool:
        return len(self.lessons) > 0
    
    @classmethod
    def create_from_lessons(cls, lessons: List[Lesson], schedule_date: Optional[date] = None) -> DailySchedule:
        """
        Создает DailySchedule из списка уроков
        
        Args:
            lessons: Список объектов Lesson
            schedule_date: Дата расписания. Если None, берется из первого урока
        
        Returns:
            DailySchedule: Объект ежедневного расписания
        """
        if not lessons and schedule_date is None:
            raise ValueError("Не указана дата расписания и нет уроков для определения даты")

        if schedule_date is None:
            if lessons[0].lesson_day:
                schedule_date = lessons[0].lesson_day.date()
            else:
                raise ValueError("Не удалось определить дату расписания из уроков")
        
        daily_schedule = cls(date=schedule_date, lessons=lessons)
        daily_schedule.sort_lessons()
        
        return daily_schedule
    
    def __repr__(self) -> str:
        return f"DailySchedule(date={self.date!r}, lessons_count={len(self.lessons)})"

    def __str__(self) -> str:
        date_str = self.date.strftime("%d.%m.%Y") if self.date else "Дата не указана"
        lessons_str = "\n".join(f"{i+1}. {lesson.start_time or '??:??'} - {str(lesson.subject or 'Нет предмета')}" 
                              for i, lesson in enumerate(self.lessons))
        
        return f"Расписание на {date_str} ({len(self.lessons)} уроков):\n{lessons_str if lessons_str else 'Уроков нет'}"