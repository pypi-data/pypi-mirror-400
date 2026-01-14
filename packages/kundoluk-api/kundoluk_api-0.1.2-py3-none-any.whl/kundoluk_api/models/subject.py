from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..utils.parsers import safe_get


@dataclass(frozen=True)
class Subject:
    """
    Модель учебного предмета
    
    Attributes:
        code: GUID предмета (уникальный идентификатор в системе)
        name: Полное название предмета (на языке по умолчанию)
        name_kg: Название предмета на кыргызском языке
        name_ru: Название предмета на русском языке
        short: Короткое название предмета (аббревиатура)
        short_kg: Короткое название на кыргызском
        short_ru: Короткое название на русском
        grade: Для какого класса предназначен предмет
    """
    code: Optional[str] = None
    name: Optional[str] = None
    name_kg: Optional[str] = None
    name_ru: Optional[str] = None
    short: Optional[str] = None
    short_kg: Optional[str] = None
    short_ru: Optional[str] = None
    grade: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["Subject"]:
        if not data:
            return None
        
        return cls(
            code=safe_get(data, 'code', str),
            name=safe_get(data, 'name', str),
            name_kg=safe_get(data, 'nameKg', str),
            name_ru=safe_get(data, 'nameRu', str),
            short=safe_get(data, 'short', str),
            short_kg=safe_get(data, 'shortKg', str),
            short_ru=safe_get(data, 'shortRu', str),
            grade=safe_get(data, 'grade', int)
        )
    
    def __repr__(self) -> str:
        return f"Subject(code={self.code!r}, name_ru={self.name!r})"

    def __str__(self) -> str:
        return f"Предмет: {self.name_ru or 'Без названия'} ({self.short_ru or 'Нет сокращения'})"

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if not isinstance(other, Subject):
            return False
        return self.code == other.code