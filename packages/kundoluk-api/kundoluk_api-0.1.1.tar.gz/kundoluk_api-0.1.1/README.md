# Документация для библиотеки `kundoluk_api`

## Обзор

Библиотека `kundoluk_api` предоставляет Python-интерфейс для взаимодействия с API электронного журнала "Кундолук" (Кыргызстан). Библиотека позволяет получать расписание уроков, оценки, домашние задания и другую информацию из системы.

**⚠️ ВАЖНОЕ ПРИМЕЧАНИЕ:** Данная библиотека работает **только для аккаунтов студентов (учеников)**. Поддержка аккаунтов учителей и родителей не реализована.

---

## Установка

```bash
pip install kundoluk_api
```

---

## Быстрый старт

### Аутентификация

```python
from kundoluk_api.api import StudentClient

# Создание клиента
client = StudentClient(
    user_name="логин_ученика",  # Обычно ПИН
    password="пароль"
)

# Аутентификация
client.authenticate()

print(f"Аутентифицирован как: {client.account}")
```

### Получение расписания

```python
from datetime import date

# Расписание на сегодня
today = date.today()
schedule = client.get_daily_schedule(today)
if schedule.is_success and schedule.data:
    print(f"Расписание на {today}:")
    for lesson in schedule.data:
        print(f"  {lesson.start_time} - {lesson.subject}: {lesson.teacher}")
```

---

## Основные компоненты

### Клиенты

Библиотека предоставляет два типа клиентов:

1. **`StudentClient`** - синхронный клиент
2. **`AsyncStudentClient`** - асинхронный клиент (требует `asyncio`)

### Модели данных

Все данные представлены в виде датаклассов:

- `KundolukAccount` - информация об ученике
- `DailySchedule` / `DailySchedules` - расписание на день/период
- `Lesson` - информация об уроке
- `Mark` / `Marks` - оценки
- `QuarterMark` / `QuarterMarks` - четвертные оценки
- И другие вспомогательные модели

---

## Подробное использование

### Инициализация клиента

```python
from kundoluk_api.api import StudentClient, AsyncStudentClient

# Синхронный клиент
sync_client = StudentClient(
    user_name="username",
    password="password",
    user_agent="MyApp/1.0",  # Опционально
    device="android"  # Опционально
)

# Асинхронный клиент
async_client = AsyncStudentClient(
    user_name="username",
    password="password"
)
```

### Получение информации об аккаунте

После аутентификации доступна информация об ученике:

```python
client.authenticate()
account = client.account

print(f"ФИО: {account.last_name} {account.first_name} {account.mid_name}")
print(f"Класс: {account.grade}{account.letter}")
print(f"Школа: {account.school.name_ru}")
print(f"ПИН: {account.pin_as_string}")
```

### Работа с расписанием

#### На конкретный день

```python
from datetime import date, timedelta

# Сегодня
schedule_today = client.get_daily_schedule(date.today())

# На конкретную дату
schedule = client.get_daily_schedule("2024-01-15")  # Можно передавать строку

if schedule.is_success and schedule.data:
    for lesson in schedule.data:
        print(f"{lesson.lesson_number}. {lesson.subject} ({lesson.start_time}-{lesson.end_time})")
        if lesson.task:
            print(f"   ДЗ: {lesson.task.name}")
        if lesson.marks:
            print(f"   Оценки: {lesson.marks}")
```

#### За период

```python
start_date = date(2024, 1, 1)
end_date = date(2024, 1, 31)

schedule_range = client.get_schedule_range(start_date, end_date)

if schedule_range.is_success:
    for daily_schedule in schedule_range.data:
        print(f"\n{date.strftime(daily_schedule.date, '%d.%m.%Y')}:")
        for lesson in daily_schedule.lessons[:3]:  # Первые 3 урока
            print(f"  - {lesson.subject}")
```

#### С оценками за четверть

```python
# Получить расписание с оценками за 1 четверть
schedule_with_marks = client.get_schedule_with_marks(term=1, absent=False)

# Получить расписание с отметками об отсутствии за 2 четверть
schedule_with_absent = client.get_schedule_with_marks(term=2, absent=True)
```

### Полное расписание (с оценками и ДЗ)

```python
# На конкретный день (15 января)
full_day_schedule = client.get_full_schedule(day=15, month=1)

if full_day_schedule:
    for lesson in full_day_schedule:
        print(f"\n{lesson.subject}:")
        if lesson.marks:
            print(f"  Оценки: {', '.join(str(mark.value) for mark in lesson.marks)}")
        if lesson.task:
            print(f"  ДЗ: {lesson.task.name}")
```

#### За всю четверть

```python
# Полное расписание за 3 четверть
full_term_schedule = client.get_full_schedule_term(term=3)

if full_term_schedule:
    for day in full_term_schedule:
        print(f"\n{day.date}:")
        for lesson in day.lessons:
            if lesson.marks:
                print(f"  {lesson.subject}: оценки - {lesson.marks}")
```

### Четвертные оценки

```python
quarter_marks = client.get_all_quarter_mark()

if quarter_marks.is_success:
    for result in quarter_marks.data:
        if result.quarter_marks:
            for mark in result.quarter_marks:
                print(f"{mark.subject_name_ru}: {mark.quarter} четв. - {mark.quarter_mark}")
```

### Смена пароля

```python
# Смена пароля с указанием текущего
result = client.change_password(
    new_password="новый_пароль",
    current_password="старый_пароль"
)

if result.is_success:
    print("Пароль успешно изменен")
    # Пароль автоматически обновляется в клиенте
else:
    print(f"Ошибка: {result.message}")
```

---

## Асинхронное использование

```python
import asyncio
from kundoluk_api.api import AsyncStudentClient

async def main():
    client = AsyncStudentClient(user_name="username", password="password")
    
    # Аутентификация
    await client.authenticate()
    
    # Получение расписания
    schedule = await client.get_daily_schedule("2024-01-15")
    
    # Параллельное получение данных
    marks_task = client.get_schedule_with_marks(1, absent=False)
    homework_task = client.get_schedule_with_homework(1)
    
    marks, homework = await asyncio.gather(marks_task, homework_task)
    
    # Работа с результатами...

asyncio.run(main())
```

---

## Обработка ошибок

### Типы исключений:

- `KundolukError` - базовое исключение библиотеки
- `APIError` - ошибки от сервера (4xx, 5xx)
- `ValidationError` - неверный логин/пароль
- `AuthError` - истекшая или отсутствующая сессия

---

## Предупреждения (Warnings)

Библиотека использует систему предупреждений Python для обработки незначительных проблем:

### Типы предупреждений:

- `ModelWarning` - общие проблемы с моделями
- `DateParseWarning` - ошибки парсинга дат
- `EnumMissingWarning` - неизвестные значения в перечислениях
- `MissingFieldWarning` - отсутствующие поля в JSON
- И другие

---

## Утилиты

### Работа с учебным годом

```python
from kundoluk_api.utils.school_year import get_quarter, get_date_in_school_year

# Определение четверти для даты
date_obj = date(2024, 10, 15)
quarter = get_quarter(date_obj)  # Вернет 1
quarter_nearest = get_quarter(date_obj, nearest=True)  # Вернет ближайшую четверть

# Получение даты в контексте учебного года
school_date = get_date_in_school_year(month=9, day=1)  # 1 сентября текущего учебного года
```

---

## Перечисления (Enums)

### Типы оценок

```python
from kundoluk_api.enums import MarkType

mark_type = MarkType.GENERAL  # Обычная оценка
mark_type = MarkType.HOMEWORK  # Домашняя работа
mark_type = MarkType.CONTROL  # Контрольная работа
```

### Типы посещаемости

```python
from kundoluk_api.enums import AbsentType

absent_type = AbsentType.PRESENT  # Присутствовал
absent_type = AbsentType.ABSENT  # Отсутствовал
absent_type = AbsentType.LATE  # Опоздал
```

---

## Примеры использования

### Пример 1: Получение всех оценок за неделю

```python
def get_week_grades(client, start_date):
    """Получить все оценки за неделю, начиная с start_date"""
    end_date = start_date + timedelta(days=6)
    
    schedule = client.get_schedule_range(start_date, end_date)
    if not schedule.is_success:
        return []
    
    all_marks = []
    for day_schedule in schedule.data:
        for lesson in day_schedule.lessons:
            if lesson.marks:
                for mark in lesson.marks:
                    all_marks.append({
                        'date': day_schedule.date,
                        'subject': lesson.subject.name_ru if lesson.subject else None,
                        'mark': mark.value,
                        'type': mark.mark_type.value
                    })
    
    return all_marks
```

### Пример 2: Статистика посещаемости

```python
def attendance_statistics(client, term):
    """Статистика посещаемости за четверть"""
    schedule = client.get_schedule_with_marks(term, absent=True)
    if not schedule.is_success:
        return None
    
    stats = {'present': 0, 'absent': 0, 'late': 0}
    
    for day_schedule in schedule.data:
        for lesson in day_schedule.lessons:
            if lesson.marks:
                for mark in lesson.marks:
                    if mark.absent_type == AbsentType.PRESENT:
                        stats['present'] += 1
                    elif mark.absent_type == AbsentType.ABSENT:
                        stats['absent'] += 1
                    elif mark.absent_type == AbsentType.LATE:
                        stats['late'] += 1
    
    return stats
```

### Пример 3: Асинхронный сбор всех данных

```python
async def get_all_student_data(client):
    """Получить все данные студента за текущий учебный год"""
    tasks = []
    
    # Сбор данных за все четверти
    for quarter in range(1, 5):
        tasks.append(client.get_full_schedule_term(quarter))
    
    tasks.append(client.get_all_quarter_mark())
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Обработка результатов...
    return results
```

---

## Ограничения и известные проблемы

1. **Только для студентов:** Библиотека не поддерживает аккаунты учителей и родителей.
2. **Текущий учебный год:** Некоторые методы работают только в рамках текущего учебного года.
3. **Ограничения API:** Библиотека зависит от ограничений оригинального API Кундолук.
4. **Неполные данные:** Не все поля всегда заполнены сервером.

---