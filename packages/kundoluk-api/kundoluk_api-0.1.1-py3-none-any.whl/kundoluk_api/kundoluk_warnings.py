class ModelWarning(Warning):
    """Общий класс для всех бед модели"""
    pass

class DateParseWarning(ModelWarning):
    """При парсинге простой даты (date)"""
    pass

class DatetimeParseWarning(ModelWarning):
    """При парсинге даты со временем (datetime)"""
    pass

class LessonParseWarning(ModelWarning):
    """При парсинге урока (Lesson)"""
    pass

class MissingFieldWarning(ModelWarning):
    """Поле отсутствует в JSON"""
    pass

class TypeConversionWarning(ModelWarning):
    """Тип данных не совпал, и пришлось преобразовывать"""
    pass

class FieldRequiredWarning(MissingFieldWarning):
    """Отсутствует поле, которое помечено как ОБЯЗАТЕЛЬНОЕ"""
    pass

class EnumWarning(Warning):
    """Общий класс для всех бед Enum"""
    pass

class EnumMissingWarning(EnumWarning):
    """Если значение не найдено в Enum"""
    def __init__(self, enum_cls, value):
        super().__init__(f"Нету значения '{value}' в Enum: {enum_cls.__name__}")