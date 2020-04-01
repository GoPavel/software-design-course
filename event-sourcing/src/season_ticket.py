import datetime
from typing import Optional


class AccountBase:
    pass


class AccountForAdmin:

    @staticmethod
    async def info(no: int) -> dict:
        pass

    @staticmethod
    async def create_season_ticket(info: dict):
        pass

    @staticmethod
    async def extend_ticket(no: int, until: datetime.date):
        pass


class Reports:

    @staticmethod
    async def count_clients_in_day(day: datetime.date) -> int:
        pass

    @staticmethod
    async def average_attendance_duration(no: int) -> datetime.timedelta:
        pass

    @staticmethod
    async def freq_attendance(no: int) -> float:
        pass

class CheckIn:

    @staticmethod
    async def check_in(no: int) -> bool:
        pass

    @staticmethod
    async def check_out(no: int):
        pass

class AccountView:
    pass
