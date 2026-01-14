from typing import Optional, Any, Dict
from datetime import datetime, date
import warnings

from ..kundoluk_warnings import (
    DateParseWarning,
    DatetimeParseWarning,
    FieldRequiredWarning,
    MissingFieldWarning, 
    TypeConversionWarning, 
    ModelWarning
)


def parse_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            formats = [
                "%Y-%m-%d",
                "%d.%m.%Y",
                "%d%m%Y",
                "%Y/%m/%d"
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.date()
                except ValueError:
                    continue
        except Exception:
            pass
    warnings.warn(f"Не удалось распарсить date: {repr(value)}", DateParseWarning, stacklevel=2)
    return None

def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            formats = [
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
    warnings.warn(f"Не удалось распарсить datetime: {repr(value)}", DatetimeParseWarning, stacklevel=2)
    return None


def safe_get(data: Dict[str, Any], key: str, expected_type: type = None, 
              default: Any = None, required: bool = False) -> Any:
    """
    Безопасное получение значения из словаря с проверкой типа
    
    Args:
        data: Исходный словарь
        key: Ключ для поиска
        expected_type: Ожидаемый тип данных
        default: Значение по умолчанию
        required: Обязательное ли поле
    
    Returns:
        Значение или default
    """
    if key not in data:
        if required:
            warnings.warn(f"Отсутствует обязательное поле: '{key}'", FieldRequiredWarning, stacklevel=2)
        else:
            warnings.warn(f"Отсутствует поле: '{key}'", MissingFieldWarning, stacklevel=2)
        return default
    
    value = data[key]
    
    if value is None:
        return None
    
    if expected_type and not isinstance(value, expected_type):
        try:
            if expected_type == int and isinstance(value, (str, float)):
                return int(float(value))
            elif expected_type == str:
                return str(value)
            elif expected_type == bool and isinstance(value, (str, int)):
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'да')
                return bool(value)
            elif expected_type == float and isinstance(value, (str, int)):
                return float(value)
            else:
                warnings.warn(
                    f"Поле '{key}': ожидался тип {expected_type.__name__}, "
                    f"получен {type(value).__name__} = {repr(value)}",
                    TypeConversionWarning,
                    stacklevel=2
                )
                return default
        except (ValueError, TypeError):
            warnings.warn(
                f"Поле '{key}': не удалось преобразовать {type(value).__name__} "
                f"в {expected_type.__name__}",
                ModelWarning,
                stacklevel=2
            )
            return default
    
    return value