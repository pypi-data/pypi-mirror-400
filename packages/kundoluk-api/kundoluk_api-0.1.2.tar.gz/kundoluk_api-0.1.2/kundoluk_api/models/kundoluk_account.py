from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Any, Dict

from ..utils.parsers import safe_get, parse_datetime

if TYPE_CHECKING:
    from . import School


@dataclass(frozen=True)
class KundolukAccount:
    """
    Модель ученика
    
    Attributes:
        user_id: UUID пользователя в системе (ученик/учитель/родитель)
        student_id: UUID конкретного ученика
        okpo: Код школы по государственному классификатору
        pin: PIN паспорта (как число, 14 цифр)
        pin_as_string: PIN паспорта как строка
        grade: Класс обучения
        letter: Буква класса (например, "В")
        last_name: Фамилия ученика
        first_name: Имя ученика
        mid_name: Отчество ученика
        email: Электронная почта (часто не заполнена)
        phone: Телефон (часто не заполнен)
        is_agreement_signed: Подписал ли пользователь пользовательское соглашение
        locale: Языковые настройки (ru/kg)
        change_password: Требуется ли смена пароля (часто при первом входе)
        role: Тип пользователя (type) - "student", "teacher", "parent"
        birthdate: Дата рождения ученика
        school: Объект школы, в которой учится ученик
    """
    user_id: Optional[str] = None
    student_id: Optional[str] = None
    okpo: Optional[str] = None
    pin: Optional[int] = None
    pin_as_string: Optional[str] = None
    grade: Optional[int] = None
    letter: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    mid_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_agreement_signed: Optional[bool] = None
    locale: Optional[str] = None
    change_password: Optional[bool] = None
    role: Optional[str] = None
    birthdate: Optional[datetime] = None
    school: Optional[School] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional[KundolukAccount]:
        from . import School

        if not data:
            return None

        school_data = safe_get(data, 'school', dict)
        school = School.from_dict(school_data)
        
        birthdate_str = safe_get(data, 'birthdate', str)
        
        return cls(
            user_id=safe_get(data, 'userId', str, required=True),
            student_id=safe_get(data, 'studentId', str),
            okpo=safe_get(data, 'okpo', str),
            pin=safe_get(data, 'pin', int),
            pin_as_string=safe_get(data, 'pinAsString', str),
            grade=safe_get(data, 'grade', int),
            letter=safe_get(data, 'letter', str),
            last_name=safe_get(data, 'last_name', str),
            first_name=safe_get(data, 'first_name', str),
            mid_name=safe_get(data, 'mid_name', str),
            email=safe_get(data, 'email', str),
            phone=safe_get(data, 'phone', str),
            is_agreement_signed=safe_get(data, 'isAgreementSigned', bool),
            locale=safe_get(data, 'locale', str),
            change_password=safe_get(data, 'changePassword', bool),
            role=safe_get(data, 'type', str),
            birthdate=parse_datetime(birthdate_str) if birthdate_str else None,
            school=school
        )
    
    def __repr__(self) -> str:
        return f"Student(user_id={self.user_id!r}, last_name={self.last_name!r}, first_name={self.first_name!r})"

    def __str__(self) -> str:
        name_parts = [self.last_name, self.first_name, self.mid_name]
        name = " ".join(filter(None, name_parts))
        grade_str = f"{self.grade}{self.letter}" if self.grade and self.letter else "Класс не указан"
        return f"Ученик: {name or 'Имя не указано'} ({grade_str})"