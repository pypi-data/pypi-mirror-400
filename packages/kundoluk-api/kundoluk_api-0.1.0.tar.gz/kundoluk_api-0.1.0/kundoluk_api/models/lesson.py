from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

from ..utils.parsers import safe_get, parse_datetime

if TYPE_CHECKING:
    from . import LessonTeacher, Subject, Room, Task, Topic, Student, Marks


@dataclass(frozen=True)
class Lesson:
    """
    Модель урока (занятия)
    
    Attributes:
        uid: Уникальный идентификатор урока
        schedule_item_id: ID урока в расписании (часто совпадает с uid)
        
        teacher: Учитель, ведущий урок
        subject: Учебный предмет
        room: Кабинет, где проходит урок
        
        start_time: Время начала урока (формат "HH:MM")
        end_time: Время окончания урока (формат "HH:MM")
        lesson_time: Длительность урока (формат "HH:MM:SS")
        lesson_day: Дата проведения урока
        year: Год проведения урока
        month: Месяц проведения урока
        day: День проведения урока
        lesson_number: Номер урока в расписании дня (1-й, 2-й и т.д.)
        
        student: Ученик
        marks: Список оценок

        topic: Тема сегодняшнего урока
        task: Задание на сегодня
        last_task: Предыдущее задание
        
        okpo: Код школы
        grade_id: UUID класса
        grade: Номер класса
        letter: Буква класса
        is_krujok: Является ли урок кружком (true/false)
        group: Номер группы (0 если нет деления)
        group_id: UUID группы
        subject_group_name: Название группы ("1 группа", "2 группа")
        
        shift: Смена (1 - первая, 2 - вторая)
        day_of_week: День недели (0-воскресенье, 1-понедельник...)
        
        school_id: UUID школы
        school_name_kg: Название школы на кыргызском
        school_name_ru: Название школы на русском
        
        is_content_subject: Содержательный ли предмет (не классный час и т.д.)
        is_twelve: Используется ли 12-балльная система оценок
        order_index: Порядковый индекс для сортировки
    """
    uid: Optional[str] = None
    schedule_item_id: Optional[str] = None
    
    teacher: Optional[LessonTeacher] = None
    subject: Optional[Subject] = None
    room: Optional[Room] = None
    
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    lesson_time: Optional[str] = None
    lesson_day: Optional[datetime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    lesson_number: Optional[int] = None

    student: Optional[Student] = None
    marks: Optional[Marks] = None

    topic: Optional[Topic] = None
    task: Optional[Task] = None
    last_task: Optional[Task] = None
    
    okpo: Optional[str] = None
    grade_id: Optional[str] = None
    grade: Optional[int] = None
    letter: Optional[str] = None
    is_krujok: Optional[bool] = None
    group: Optional[int] = None
    group_id: Optional[str] = None
    subject_group_name: Optional[str] = None
    
    shift: Optional[int] = None
    day_of_week: Optional[int] = None
    
    school_id: Optional[str] = None
    school_name_kg: Optional[str] = None
    school_name_ru: Optional[str] = None
    
    is_content_subject: Optional[bool] = None
    is_twelve: Optional[bool] = None
    order_index: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional[Lesson]:
        from . import LessonTeacher, Subject, Room, Task, Topic, Student, Marks
        
        if not data:
            return None

        teacher_data = safe_get(data, 'teacher', dict)
        teacher = LessonTeacher.from_dict(teacher_data)
        
        subject_data = safe_get(data, 'subject', dict)
        subject = Subject.from_dict(subject_data)
        
        room_data = safe_get(data, 'roomData', dict)
        room = Room.from_dict(room_data)
        
        student_data = safe_get(data, 'student', dict)
        student = Student.from_dict(student_data)

        marks_data = safe_get(data, 'marks', list)
        marks = Marks.from_dict(marks_data)

        topic_data = safe_get(data, 'topic', dict)
        topic = Topic.from_dict(topic_data)
        
        task_data = safe_get(data, 'task', dict)
        task = Task.from_dict(task_data)
        
        last_task_data = safe_get(data, 'lastTask', dict)
        last_task = Task.from_dict(last_task_data)
        
        lesson_day_str = safe_get(data, 'lessonDay', str)
        lesson_day = parse_datetime(lesson_day_str) if lesson_day_str else None
        
        return cls(
            uid=safe_get(data, 'uid', str),
            schedule_item_id=safe_get(data, 'scheduleItemId', str),
            teacher=teacher,
            subject=subject,
            room=room,
            start_time=safe_get(data, 'startTime', str),
            end_time=safe_get(data, 'endTime', str),
            lesson_time=safe_get(data, 'lessonTime', str),
            lesson_day=lesson_day,
            year=safe_get(data, 'year', int),
            month=safe_get(data, 'month', int),
            day=safe_get(data, 'day', int),
            lesson_number=safe_get(data, 'lesson', int),
            marks=marks,
            student=student,
            topic=topic,
            task=task,
            last_task=last_task,
            okpo=safe_get(data, 'okpo', str),
            grade_id=safe_get(data, 'gradeId', str),
            grade=safe_get(data, 'grade', int),
            letter=safe_get(data, 'letter', str),
            is_krujok=safe_get(data, 'isKrujok', bool),
            group=safe_get(data, 'group', int),
            group_id=safe_get(data, 'groupId', str),
            subject_group_name=safe_get(data, 'subjectGroupName', str),
            shift=safe_get(data, 'shift', int),
            day_of_week=safe_get(data, 'dayOfWeek', int),
            school_id=safe_get(data, 'school', str),
            school_name_kg=safe_get(data, 'schoolNameKg', str),
            school_name_ru=safe_get(data, 'schoolNameRu', str),
            is_content_subject=safe_get(data, 'isContentSubject', bool),
            is_twelve=safe_get(data, 'isTwelve', bool),
            order_index=safe_get(data, 'orderIndex', int)
        )
    
    def __repr__(self) -> str:
        return f"Lesson(uid={self.uid!r}, subject={self.subject!r}, lesson_day={self.lesson_day!r})"

    def __str__(self) -> str:
        time_str = f"{self.start_time}-{self.end_time}" if self.start_time and self.end_time else "Время не указано"
        day_str = self.lesson_day.strftime("%d.%m.%Y") if self.lesson_day else "Дата не указана"
        
        subject_str = str(self.subject) if self.subject else "Предмет не указан"
        teacher_str = str(self.teacher) if self.teacher else "Учитель не указан"
        room_str = str(self.room) if self.room else "Кабинет не указан"
        
        return f"Урок: {subject_str}\n" \
               f"  Время: {time_str} ({day_str})\n" \
               f"  Учитель: {teacher_str}\n" \
               f"  Кабинет: {room_str}"
    
    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Lesson):
            return False
        return self.uid == other.uid