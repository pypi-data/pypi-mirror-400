from typing import Optional, Union
from datetime import date

from .parsers import parse_date


SCHOOL_QUARTERS = {
    1: {"start": (9, 1),   "end": (11, 4)},
    2: {"start": (11, 10), "end": (12, 30)},
    3: {"start": (1, 12),  "end": (3, 20)},
    4: {"start": (3, 24),  "end": (5, 31)},
}

def get_quarter(target_date: Union[date, str], nearest: bool = False) -> Optional[int]:
    """
    Определяет принадлежность даты к учебной четверти в Кыргызстане.

    Args:
        target_date (date): Объект даты для проверки.
        nearest (bool): Если True, при попадании на каникулы вернет номер ближайшей четверти.
                        Если False, вернет None.

    Returns:
        int: Номер четверти.
        None: Каникулы.
    """
    target_date = parse_date(target_date)
    
    current_school_year = target_date.year if target_date.month >= 9 else target_date.year - 1
    
    q_dates = {}
    for q, dates in SCHOOL_QUARTERS.items():
        year = current_school_year if q <= 2 else current_school_year + 1
        q_dates[q] = (
            date(year, *dates["start"]), 
            date(year, *dates["end"])
        )

    for q_num, (start, end) in q_dates.items():
        if start <= target_date <= end:
            return q_num

    if not nearest:
        return None

    diffs = []
    for q_num, (start, end) in q_dates.items():
        diff_start = abs((target_date - start).days)
        diff_end = abs((target_date - end).days)
        diffs.append((min(diff_start, diff_end), q_num))

    return min(diffs, key=lambda x: x[0])[1]


def get_date_in_school_year(month: int, day: int, target_date: Optional[Union[date, str]] = None) -> date:
    if target_date:
        reference_date = parse_date(target_date)
    else:
        reference_date = date.today()

    school_year_start = reference_date.year if reference_date.month >= 9 else reference_date.year - 1
    
    result_year = school_year_start if month >= 9 else school_year_start + 1
    
    return date(result_year, month, day)