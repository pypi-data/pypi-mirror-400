from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..utils.parsers import safe_get


@dataclass(frozen=True)
class Room:
    """
    Модель кабинета (аудитории)
    
    Attributes:
        id_room: GUID кабинета (уникальный идентификатор)
        room_name: Номер кабинета (например, "225")
        floor: Этаж, на котором находится кабинет
        block: Блок/корпус здания (если есть несколько зданий)
    """
    id_room: Optional[str] = None
    room_name: Optional[str] = None
    floor: Optional[int] = None
    block: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["Room"]:
        if not data:
            return None
        
        return cls(
            id_room=safe_get(data, 'id', str),
            room_name=safe_get(data, 'roomName', str),
            floor=safe_get(data, 'floor', int),
            block=safe_get(data, 'block', str)
        )
    
    def __repr__(self) -> str:
        return f"Room(id_room={self.id_room!r}, room_name={self.room_name!r})"

    def __str__(self) -> str:
        floor_str = f", этаж {self.floor}" if self.floor is not None else ""
        block_str = f", блок {self.block}" if self.block else ""
        return f"Кабинет: {self.room_name or 'Номер не указан'}{floor_str}{block_str}"
    
    def __hash__(self):
        return hash(self.id_room)

    def __eq__(self, other):
        if not isinstance(other, Room):
            return False
        return self.id_room == other.id_room