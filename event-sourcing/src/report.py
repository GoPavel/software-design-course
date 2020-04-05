import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta, date

import motor.motor_asyncio as aiomotor
import schematics

from store import EventReader
from turnstile import TurnstileEventType

logger = logging.getLogger("report")


class DayReport(schematics.Model):
    day = schematics.types.DateTimeType(serialized_format='%Y-%m-%d %H:%M:%S', drop_tzinfo=True)
    mean_visit_duration = schematics.types.FloatType()  # in minutes
    visit_freq = schematics.types.FloatType()  # amount of visit in hour

    # latest_event_timestamp = schematics.types.TimestampType()

    @classmethod
    def get_empty(cls, day: date):
        return cls({
            'day': str(datetime.combine(day, datetime.min.time())),
            'mean_visit_duration': 0,
            'visit_freq': 0,
        })


class ReportStore:
    def __init__(self, name: str):
        self._mongo_client = aiomotor.AsyncIOMotorClient('localhost', 27017)
        self._db = self._mongo_client[name]
        self._day_report_coll = self._db['day-report']

    async def get_or_create_day_report(self, t: datetime) -> DayReport:
        day = t.date()
        report = await self._day_report_coll.find_one({'day': str(day)})
        if report is None:
            logger.debug(f'Not found day report on {day}, creating new')
            report = DayReport.get_empty(day)
            await self._day_report_coll.insert_one(report.to_primitive())
        return report

    async def upload_report(self, report: DayReport):
        await self._day_report_coll.delete_one({'day': str(report.day.date())})
        await self._day_report_coll.insert_one(report.to_primitive())


class ReportService:
    def __init__(self, report_store: ReportStore, event_store: EventReader):
        self.reports = report_store
        self.events = event_store

    async def update_day(self, day: date) -> DayReport:
        """
        Recalculate statistic report for that day and upload new report in store.
        :return: New report
        """
        from_time = datetime.combine(day, datetime.min.time())
        to_time = datetime.combine(day, datetime.max.time())
        visits = dict()
        durations = []
        async for event in self.events.find_all(from_time=from_time, to_time=to_time):
            if event.type == TurnstileEventType.CameIn:
                visits[event.object_name] = event
            elif event.type == TurnstileEventType.Leave:
                if event.object_name in visits:
                    from_time = visits[event.object_name].timestamp
                    to_time = event.timestamp
                    durations.append((to_time - from_time).seconds // 60)
                    del visits[event.object_name]

        report = DayReport.get_empty(day)
        report.mean_visit_duration = 0 if not durations else sum(durations) / len(durations)
        report.visit_freq = len(durations) / 24
        await self.reports.upload_report(report)
        return report


async def main(args):
    if args.command == 'update':
        report_store = ReportStore('event-source-hw')
        event_store = EventReader(db_name='event-source-hw')
        rep = ReportService(report_store, event_store)
        t = datetime.now()
        days = [(t - timedelta(days=i)).date() for i in range(3)]
        for day in days:
            report = await rep.update_day(day)
            print(report.to_primitive())
    else:
        raise RuntimeError("Wrong sub-command")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser(description="Statistic report client")
    subparsers = parser.add_subparsers(dest='command', help="sub-command help")

    update_parser = subparsers.add_parser('update', help="update reports in store (last 3 days)")
    # update_parser.add_argument('--from') TODO

    asyncio.run(main(parser.parse_args()))
