from dataclasses import dataclass
from typing import TypeVar, Generic, Optional


T = TypeVar('T')

@dataclass(frozen=True)
class KundolukResponse(Generic[T]):
    """Универсальная модель ответа от API Kundoluk"""
    result_code: int
    message: str
    data: Optional[T] = None

    @property
    def is_success(self) -> bool:
        return self.result_code == 0