from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..utils.parsers import safe_get


@dataclass(frozen=True)
class School:
    """
    Модель школы (образовательного учреждения)
    
    Attributes:
        school_id: UUID школы (уникальный идентификатор в системе)
        institution_id: UUID вышестоящего учреждения (обычно нулевой GUID)
        okpo: Код школы по государственному классификатору (8 цифр)
        name_ru: Полное название школы на русском языке
        short_name: Сокращенное название школы
        is_staff_active: Активен ли персонал школы в системе
    """
    school_id: Optional[str] = None
    institution_id: Optional[str] = None
    okpo: Optional[str] = None
    name_ru: Optional[str] = None
    short_name: Optional[str] = None
    is_staff_active: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["School"]:
        if not data:
            return None
        
        return cls(
            school_id=safe_get(data, 'schoolId', str),
            institution_id=safe_get(data, 'institutionId', str),
            okpo=safe_get(data, 'okpo', str),
            name_ru=safe_get(data, 'nameRu', str),
            short_name=safe_get(data, 'short', str),
            is_staff_active=safe_get(data, 'isStaffActive', bool)
        )
    
    def __repr__(self) -> str:
        return f"School(school_id={self.school_id!r}, name_ru={self.name_ru!r}, okpo={self.okpo!r})"

    def __str__(self) -> str:
        return f"Школа: {self.name_ru or 'Без названия'} (ОКПО: {self.okpo or 'Нет кода'})"

    def __hash__(self):
        return hash(self.school_id)

    def __eq__(self, other):
        if not isinstance(other, School):
            return False
        return self.school_id == other.school_id