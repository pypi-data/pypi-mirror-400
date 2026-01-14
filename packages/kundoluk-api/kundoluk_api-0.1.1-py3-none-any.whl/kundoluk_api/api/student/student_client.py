from typing import Optional, Union
from datetime import date

from ..clients import sync_client
from .base_student import BaseStudent
from ...utils.parsers import parse_date
from ...utils.school_year import get_date_in_school_year, get_quarter, SCHOOL_QUARTERS
from ...models import KundolukResponse, KundolukAccount, DailySchedules, DailySchedule, QuarterMarksResults


class StudentClient(BaseStudent):
    def authenticate(self):
        super().authenticate()
        
        response = sync_client.post(
            url=self._login_url,
            headers=self._login_headers,
            json=self._login_json
        )

        data = self._handle_response(response)

        self.bearer_token = data.get("token")

        self.account = KundolukAccount.from_dict(data)

    def change_password(self, new_password, current_password: Optional[str] = None):
        super().change_password(new_password, current_password)
        if current_password is None:
            current_password = self.password
        
        response = sync_client.post(
            url=self._change_password_url,
            headers=self._headers,
            json=self._get_change_password_json(new_password, current_password)
        )

        data = self._handle_response(response)

        if data.get("resultCode") == 0:
            self.password = new_password

        return KundolukResponse(data.get("resultCode"), data.get("resultMessage"))
    
    def get_daily_schedule(
        self,
        target_date: Union[date, str],
    ) -> KundolukResponse[Optional[DailySchedule]]:
        
        target_date = parse_date(target_date)
        
        response = sync_client.get(
            url=self._get_schedule_url.format(target_date, target_date),
            headers=self._headers
        )
        data = self._handle_response(response)
        
        daily_schedule = DailySchedules.from_dict(data.get("actionResult"))
        
        return KundolukResponse(
            data.get("resultCode"),
            data.get("resultMessage"),
            daily_schedule[0] if daily_schedule else None
        )
    
    def get_schedule_range(
        self, 
        start_date: Union[date, str], 
        end_date: Union[date, str]
    ) -> KundolukResponse[DailySchedules]:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        response = sync_client.get(
            url=self._get_schedule_url.format(start_date, end_date),
            headers=self._headers
        )
        data = self._handle_response(response)

        return KundolukResponse(
            data.get("resultCode"),
            data.get("resultMessage"), 
            DailySchedules.from_dict(data.get("actionResult"))
        )

    def get_schedule_with_marks(
        self,
        term: int,
        absent: bool = False
    ) -> KundolukResponse[DailySchedules]:
        response = sync_client.get(
            url=self._get_marks_url.format(term, int(absent)),
            headers=self._headers
        )
        data = self._handle_response(response)

        return KundolukResponse(
            data.get("resultCode"),
            data.get("resultMessage"), 
            DailySchedules.from_dict(data.get("actionResult"))
        )
    
    def get_full_schedule(self, day: int, month: int) -> Optional[DailySchedule]:
        target_date = get_date_in_school_year(month, day)
        
        base = self.get_daily_schedule(target_date)
        if not base.is_success or not base.data: return None
        
        marks = self.get_schedule_with_marks(get_quarter(target_date), absent=False).data
        absent = self.get_schedule_with_marks(get_quarter(target_date), absent=True).data

        extra_days = [
            ds for ds in [marks.get_by_date(target_date), absent.get_by_date(target_date)] 
            if ds
        ]

        full_data = base.data.merge_extra_mark_data(extra_days)

        return full_data
    
    def get_full_schedule_term(self, term: int) -> Optional[DailySchedules]:
        if term > 4 or term < 1:
            raise ValueError(f"Такой четверти не существует: {term}")
        
        start_date = get_date_in_school_year(*SCHOOL_QUARTERS[term]["start"])
        end_date = get_date_in_school_year(*SCHOOL_QUARTERS[term]["end"]) 

        base = self.get_schedule_range(start_date, end_date)
        if not base.is_success or not base.data: return None
        
        marks = self.get_schedule_with_marks(term, absent=False)
        absent = self.get_schedule_with_marks(term, absent=True)
        
        extra_data = []
        if marks.data: extra_data.append(marks.data)
        if absent.data: extra_data.append(absent.data)

        return base.data.merge_quarter_marks(extra_data)
    
    def get_schedule_with_homework(self, term: int) -> KundolukResponse[DailySchedules]:
        response = sync_client.get(
            url=self._get_homework_url.format(term),
            headers=self._headers
        )
        data = self._handle_response(response)

        return KundolukResponse(
            data.get("resultCode"),
            data.get("resultMessage"), 
            DailySchedules.from_dict(data.get("actionResult"))
        )
    
    def get_all_quarter_mark(self) -> KundolukResponse[QuarterMarksResults]:
        response = sync_client.get(
            url=self._get_all_quarter_mark_url,
            headers=self._headers
        )
        data = self._handle_response(response)

        return KundolukResponse(
            data.get("resultCode"),
            data.get("resultMessage"), 
            QuarterMarksResults.from_dict(data.get("actionResult"))
        )