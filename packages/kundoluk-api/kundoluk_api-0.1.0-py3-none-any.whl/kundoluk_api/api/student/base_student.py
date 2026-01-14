from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Union

import httpx

from ..clients import host
from ...models import KundolukResponse, KundolukAccount, DailySchedules, DailySchedule, QuarterMarksResults
from ...exceptions import ValidationError, APIError, AuthError


class BaseStudent(ABC):
    _kundoluk_api_url = "https://kundoluk.edu.gov.kg/api/"
    _login_url = _kundoluk_api_url + "auth/loginStudent"
    _change_password_url = _kundoluk_api_url + "account/changePasswordStudent"
    _get_schedule_url = _kundoluk_api_url + "student/gradebook/list?start_date={}&end_date={}"
    _get_marks_url = _kundoluk_api_url + "student/gradebook/term/{}?absent={}"
    _get_homework_url = _kundoluk_api_url + "student/homework/list?term_no={}"
    _get_all_quarter_mark_url = _kundoluk_api_url + "student/qmarks/all"

    def __init__(
            self,
            user_name: Optional[str] = None,
            password: Optional[str] = None,
            bearer_token: Optional[str] = None,
            fcm_token: Optional[str] = None,
            user_agent: Optional[str] = None, #"Dart/3.9 (dart:io)"
            device: Optional[str] = None, #"android"
            account: Optional[KundolukAccount] = None,
            accept_encoding: str = "gzip"
        ):
        self.user_name = user_name
        self.password = password
        self.bearer_token = bearer_token
        self.fcm_token = fcm_token
        self.user_agent = user_agent
        self.device = device
        self.accept_encoding = accept_encoding
        self.account: Optional[KundolukAccount] = account

    @property
    def _headers(self) -> dict:
        payload = {
            "accept-encoding": self.accept_encoding,
            "authorization": "Bearer " + self.bearer_token,
            "content-type": "application/json",
            "host": host
        }
        if not self.user_agent is None: payload["user-agent"] = self.user_agent

        return payload
    
    @property
    def _login_headers(self) -> dict:
        payload = {
            "accept-encoding": self.accept_encoding,
            "content-type": "application/json",
            "host": host
        }
        if not self.user_agent is None: payload["user-agent"] = self.user_agent

        return payload
    
    @property
    def _login_json(self) -> dict:
        payload = {
            "username": self.user_name,
            "password": self.password
        }

        if not self.device is None: payload["device"] = self.device
        if not self.fcm_token is None: payload["fcm_token"] = self.fcm_token

        return payload
    
    def _get_change_password_json(self, new_password, current_password) -> dict:
        return {
            "CurrentPassword": current_password,
            "NewPassword": new_password,
            "NewPasswordConfirmation": new_password
        }
    
    def _handle_response(self, response: httpx.Response) -> dict:
        if response.status_code == 200:
            return response.json()
        
        if response.status_code == 401:
            raise AuthError()

        error_message = "Произошла ошибка HTTP"
        try:
            error_data = response.json()
            if isinstance(error_data, list):
                error_message = "; ".join([f"{err.get('errorMessage')}" for err in error_data])
            else:
                error_message = error_data.get("message") or error_message
        except:
            error_message = response.text or error_message

        if response.status_code == 400:
            raise ValidationError(error_message)
        raise APIError(error_message, response.status_code)

    @abstractmethod
    def authenticate(self):
        """
        Выполняет аутентификацию пользователя в системе Kundoluk.
        Обновляет bearer_token и инициализирует данные аккаунта.
        """
        if not self.user_name or not self.password:
            raise ValueError("Требуются user_name и password для логина")

    @abstractmethod
    def change_password(self, new_password, current_password: Optional[str] = None) -> KundolukResponse[None]:
        """
        Изменяет текущий пароль пользователя.
        
        Args:
            new_password (str): Новый пароль.
            current_password (Optional[str]): Текущий пароль. Если не указан, используется пароль из аттрибутов класса.
        """
        if not current_password:
            if not self.password:
                raise ValueError("Требуеться self.password или передать current_password для изменение пароля")
        if not new_password:
            raise ValueError("Требуеться new_password для изменение пароля")
        
    @abstractmethod
    def get_daily_schedule(
        self,
        target_date: Union[date, str],
    ) -> KundolukResponse[Optional[DailySchedule]]:
        """Получение расписания на конкретный день.
        
        Возвращает расписание без информации об учениках и оценках.
        
        Args:
            target_date: Дата для получения расписания (date или строка)
            
        Returns:
            KundolukResponse: Объект ответа с расписанием на день или None
        """
        pass
        
    @abstractmethod
    def get_schedule_range(
        self,
        start_date: Union[date, str], 
        end_date: Union[date, str]
    ) -> KundolukResponse[DailySchedules]:
        """Получение расписания за диапазон дат.
        
        Возвращает расписание без информации об учениках и оценках.
        
        Args:
            start_date: Начальная дата диапазона
            end_date: Конечная дата диапазона
            
        Returns:
            KundolukResponse: Объект ответа с расписанием за период
        """
        pass
        
    @abstractmethod
    def get_schedule_with_marks(
        self,
        term: int,
        absent: bool = True
    ) -> KundolukResponse[DailySchedules]:
        """Получение расписания с оценками или пометками за указанную четверть.
        
        Работает только за текущий учебный год.
        Возвращает только те уроки, в которых есть оценки/пометки.
        Отсутствуют поля, связанные с домашними заданиями.
        
        Args:
            term: Номер четверти (1-4)
            absent: 
                False - получить оценки за уроки
                True - получить пометки об опозданиях/пропусках уроков
                
        Returns:
            KundolukResponse: Объект ответа с расписанием, содержащим оценки/пометки
        """
        pass
    
    @abstractmethod
    def get_full_schedule(
        self,
        day: int,
        month: int
    ) -> Optional[DailySchedule]:
        """Получение полного расписания на конкретный день.
        
        Комбинирует данные из нескольких источников:
        - Основное расписание (get_daily_schedule)
        - Оценки (get_schedule_with_marks с absent=False)
        - Пометки (get_schedule_with_marks с absent=True)
        
        Результирующий объект содержит полную информацию:
        - Основные данные урока
        - Домашние задания
        - Оценки
        - Пометки об отсутствии/опоздании
        
        Работает только за текущий учебный год.
        
        Args:
            day: День месяца
            month: Месяц
            
        Returns:
            DailySchedule: Полный объект расписания на день или None
        """

    @abstractmethod
    def get_full_schedule_term(self, term: int) -> Optional[DailySchedules]:
        """Получение полного расписания за всю четверть.
        
        Комбинирует данные из нескольких источников:
        - Основное расписание (get_daily_schedule)
        - Оценки (get_schedule_with_marks с absent=False)
        - Пометки (get_schedule_with_marks с absent=True)
        
        Результирующий объект содержит полную информацию:
        - Основные данные урока
        - Домашние задания
        - Оценки
        - Пометки об отсутствии/опоздании
        
        Работает только за текущий учебный год.
        
        Args:
            term: Номер четверти (1-4)
            
        Returns:
            DailySchedules: Полный объект расписания за четверть или None в случае ошибки
            
        Raises:
            ValueError: Если номер четверти не в диапазоне 1-4
        """
        pass
        
    @abstractmethod
    def get_schedule_with_homework(self, term: int) -> KundolukResponse[DailySchedules]:
        """Получение расписания с домашними заданиями за указанную четверть.
        
        Работает только за текущий учебный год.
        Возвращает только те уроки, в которых заданы домашние задания.
        Отсутствуют поля, связанные с оценками.
        
        Args:
            term: Номер четверти (1-4)
            
        Returns:
            KundolukResponse: Объект ответа с расписанием, содержащим домашние задания
        """
        pass

    @abstractmethod
    def get_all_quarter_mark(self) -> KundolukResponse[QuarterMarksResults]:
        """Получение четвертных оценок за текущий учебный год.
        
        Возвращает оценки за все четверти.
        В оригинальном API оценки часто дублируются - в возвращаемом объекте
        дубликаты удалены.
        
        Returns:
            KundolukResponse: Объект ответа с четвертными оценками
        """
        pass