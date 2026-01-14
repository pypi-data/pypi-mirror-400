from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List

from ..utils.parsers import safe_get, parse_datetime, parse_date


@dataclass(frozen=True)
class Student:
    """
    Контекстная информация об ученике в рамках конкретного урока.
    
    Attributes:
        grade_name: Название класса (часто null)
        schedule_item_id: UUID элемента расписания
        lesson_day: Дата урока в формате datetime (часто "0001-01-01T00:00:00" если не используется)
        lesson_day_as_date_only: Дата урока только дата (часто "0001-01-01")
        marks: Оценки за урок (дублируются в основном массиве, часто null)
        marks_for_today: Оценки за сегодня (часто null)
        object_id: UUID ученика (эквивалент student_id)
        school_id: UUID школы (часто "00000000-0000-0000-0000-000000000000")
        grade_id: UUID класса (часто null)
        okpo: Код школы (дублируется из основной информации)
        pin: PIN ученика как число
        pin_as_string: PIN как строка (часто null)
        grade: Номер класса
        letter: Буква класса
        name: Имя для отображения (часто совпадает с first_name)
        last_name: Фамилия
        first_name: Имя
        mid_name: Отчество в сокращенном формате (например, "Советбеков У. Б.")
        email: Email (часто null)
        phone: Телефон (часто null)
        group_id: ID группы (для разделения на подгруппы, например, для языков)
        subject_group_name: Название группы (например, "1 группа")
        teacher: Информация об учителе (часто null, так как есть отдельный объект teacher)
        district_name: Название района (часто null)
        city_name: Название города (часто null)
    """
    
    schedule_item_id: Optional[str] = None
    lesson_day: Optional[datetime] = None
    lesson_day_as_date_only: Optional[date] = None
    
    marks: Optional[List[Any]] = field(default=None, repr=False)
    marks_for_today: Optional[List[Any]] = field(default=None, repr=False)
    
    object_id: Optional[str] = None
    school_id: Optional[str] = None
    grade_id: Optional[str] = None
    okpo: Optional[str] = None
    
    pin: Optional[int] = None
    pin_as_string: Optional[str] = None
    grade: Optional[int] = None
    letter: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    mid_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    grade_name: Optional[str] = None
    group_id: Optional[str] = None
    subject_group_name: Optional[str] = None
    
    teacher: Optional[Any] = field(default=None, repr=False)
    district_name: Optional[str] = None
    city_name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> Optional[Student]:
        if not data:
            return None
        
        lesson_day_str = safe_get(data, 'lessonDay', str)
        lesson_day_date_str = safe_get(data, 'lessonDayAsDateOnly', str)
        
        lesson_day = None
        if lesson_day_str and lesson_day_str != "0001-01-01T00:00:00":
            lesson_day = parse_datetime(lesson_day_str)
        
        lesson_day_as_date_only = None
        if lesson_day_date_str and lesson_day_date_str != "0001-01-01":
            lesson_day_as_date_only = parse_date(lesson_day_date_str)
        
        return cls(
            schedule_item_id=safe_get(data, 'scheduleItemId', str),
            lesson_day=lesson_day,
            lesson_day_as_date_only=lesson_day_as_date_only,
            
            marks=safe_get(data, 'marks', list),
            marks_for_today=safe_get(data, 'marksForToday', list),
            
            object_id=safe_get(data, 'objectId', str),
            school_id=safe_get(data, 'schoolId', str),
            grade_id=safe_get(data, 'gradeId', str),
            okpo=safe_get(data, 'okpo', str),
            
            pin=safe_get(data, 'pin', int),
            pin_as_string=safe_get(data, 'pinAsString', str),
            grade=safe_get(data, 'grade', int),
            letter=safe_get(data, 'letter', str),
            name=safe_get(data, 'name', str),
            last_name=safe_get(data, 'lastName', str),
            first_name=safe_get(data, 'firstName', str),
            mid_name=safe_get(data, 'midName', str),
            email=safe_get(data, 'email', str),
            phone=safe_get(data, 'phone', str),
            
            grade_name=safe_get(data, 'gradeName', str),
            group_id=safe_get(data, 'groupId', str),
            subject_group_name=safe_get(data, 'subjectGroupName', str),
            
            teacher=safe_get(data, 'teacher', dict),
            district_name=safe_get(data, 'districtName', str),
            city_name=safe_get(data, 'cityName', str)
        )
    
    def __str__(self) -> str:
        return f"Ученик: {self.name} ({self.grade_name}) [{self.subject_group_name}]"
    
    def __hash__(self):
        return hash(self.pin)

    def __eq__(self, other):
        if not isinstance(other, Student):
            return False
        return self.pin == other.pin