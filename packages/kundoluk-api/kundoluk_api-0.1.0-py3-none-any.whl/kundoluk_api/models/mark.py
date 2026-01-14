from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Dict
from datetime import datetime

from ..utils.parsers import safe_get, parse_datetime
from ..enums import MarkType, AbsentType

if TYPE_CHECKING:
    from . import Subject, LessonTeacher, Student, Topic, Task


@dataclass(frozen=True)
class Mark:
    """
    Модель оценки
    
    Attributes:
        mark_id: Уникальный ID оценки
        ls_uid: ID урока (scheduleItemId)
        uid: Уникальный ID записи оценки
        student_id: UUID ученика
        student_pin: PIN ученика (число)
        student_pin_as_string: PIN ученика (строка)
        first_name: Полное ФИО ученика
        last_name: Фамилия ученика
        mid_name: Отчество ученика
        
        value: Числовое значение оценки (1-5, или 0 для пропуска)
        mark_type: Тип оценки (general, control, homework, test)
        old_mark: Предыдущее значение оценки (если изменялась)
        custom_mark: Специальная отметка (например, 'i' - болезнь)
        
        is_absent: Отсутствовал ли ученик
        absent_type: Тип отсутствия (болезнь, пропуск и т.д.)
        absent_reason: Причина отсутствия
        late_minutes: Количество минут опоздания
        
        note: Комментарий учителя
        created_at: Дата и время создания записи
        updated_at: Дата и время обновления записи
        
        subject: Предмет (часто null, так как есть в уроке)
        topic: Тема (часто null, так как есть в уроке)
        task: Задание (часто null, так как есть в уроке)
        teacher: Учитель (часто null, так как есть в уроке)
        student: Объект ученика (часто null)
        
        success: Успешность операции (часто false)
    """
    mark_id: Optional[str] = None
    ls_uid: Optional[str] = None
    uid: Optional[str] = None
    student_id: Optional[str] = None
    student_pin: Optional[int] = None
    student_pin_as_string: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mid_name: Optional[str] = None
    
    value: Optional[int] = None
    mark_type: Optional[MarkType] = None
    old_mark: Optional[int] = None
    custom_mark: Optional[str] = None
    
    is_absent: Optional[bool] = None
    absent_type: Optional[AbsentType] = None
    absent_reason: Optional[str] = None
    late_minutes: Optional[int] = None
    
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    subject: Optional[Subject] = None
    topic: Optional[Topic] = None
    task: Optional[Task] = None
    teacher: Optional[LessonTeacher] = None
    student: Optional[Student] = None
    
    success: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> Optional[Mark]:
        from . import Subject, LessonTeacher, Student, Topic, Task
        
        if not data:
            return None
        
        mark_type_str = safe_get(data, 'mark_type', str)
        mark_type = MarkType(mark_type_str)
        
        absent_type_str = safe_get(data, 'absent_type', str)
        absent_type = AbsentType(absent_type_str)
        
        created_at = parse_datetime(safe_get(data, 'created_at', str))
        updated_at = parse_datetime(safe_get(data, 'updated_at', str))

        teacher_data = safe_get(data, 'teacher', dict)
        teacher = LessonTeacher.from_dict(teacher_data)
        
        subject_data = safe_get(data, 'subject', dict)
        subject = Subject.from_dict(subject_data)

        topic_data = safe_get(data, 'topic', dict)
        topic = Topic.from_dict(topic_data)
        
        task_data = safe_get(data, 'task', dict)
        task = Task.from_dict(task_data)
        
        student_data = safe_get(data, 'student', dict)
        student = Student.from_dict(student_data)
        
        return cls(
            mark_id=safe_get(data, 'mark_id', str),
            ls_uid=safe_get(data, 'ls_uid', str),
            uid=safe_get(data, 'uid', str),
            student_id=safe_get(data, 'idStudent', str),
            student_pin=safe_get(data, 'student_pin', int),
            student_pin_as_string=safe_get(data, 'student_pin_as_string', str),
            first_name=safe_get(data, 'first_name', str),
            last_name=safe_get(data, 'last_name', str),
            mid_name=safe_get(data, 'mid_name', str),
            
            value=safe_get(data, 'mark', int),
            mark_type=mark_type,
            old_mark=safe_get(data, 'old_mark', int),
            custom_mark=safe_get(data, 'custom_mark', str),
            
            is_absent=safe_get(data, 'absent', bool),
            absent_type=absent_type,
            absent_reason=safe_get(data, 'absent_reason', str),
            late_minutes=safe_get(data, 'late_minutes', int),
            
            note=safe_get(data, 'note', str),
            created_at=created_at,
            updated_at=updated_at,
            
            subject=subject,
            topic=topic,
            task=task,
            teacher=teacher,
            student=student,
            
            success=safe_get(data, 'success', bool)
        )
    
    def __repr__(self) -> str:
        return f"Mark(value={self.value!r}, mark_type={self.mark_type!r}, created_at={self.created_at!r})"

    def __str__(self) -> str:
        if self.value:
            value_str = f"Оценка: {self.value}"
        elif self.custom_mark:
            value_str = f"Отметка: {self.custom_mark}"
        elif self.is_absent:
            value_str = "Отметка: Н"
        else:
            value_str = "Нет оценки"
        
        type_str = f" ({self.mark_type.value})" if self.mark_type else ""
        date_str = f" от {self.created_at.strftime('%d.%m.%Y %H:%M')}" if self.created_at else ""
        
        return f"{value_str}{type_str}{date_str}"
    
    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if not isinstance(other, Mark):
            return False
        return self.uid == other.uid