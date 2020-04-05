from datetime import datetime, timedelta

import pytest
from asynctest import MagicMock
from asynctest.mock import CoroutineMock, Mock

from report import ReportService
from store import EventReader
from turnstile import TurnstileEventType, CameInEvent, LeaveEvent


@pytest.mark.asyncio
async def test_update_day():
    store = Mock(EventReader)
    store.find_all = Mock(return_value=MagicMock())
    t1 = datetime.fromtimestamp(1)
    dt1 = timedelta(minutes=30)
    t2 = datetime.fromtimestamp(2)
    dt2 = timedelta(minutes=60)
    store.find_all.return_value.__aiter__.return_value = [
        CameInEvent({
            'type': TurnstileEventType.CameIn,
            'object_name': '1',
            'timestamp': t1,
            'client_name': 'turnstile'
        }),
        CameInEvent({
            'type': TurnstileEventType.CameIn,
            'object_name': '2',
            'timestamp': t2,
            'client_name': 'turnstile'
        }),
        LeaveEvent({
            'type': TurnstileEventType.Leave,
            'object_name': '1',
            'timestamp': t1 + dt1,
            'client_name': 'turnstile'
        }),
        LeaveEvent({
            'type': TurnstileEventType.Leave,
            'object_name': '2',
            'timestamp': t2 + dt2,
            'client_name': 'turnstile'
        }),
    ]

    reports = Mock()
    reports.upload_report = CoroutineMock()
    report = await ReportService(reports, store).update_day(t1.date())

    reports.upload_report.assert_awaited_with(report)
    assert report.to_primitive() == {
        'day': str(datetime.combine(t1.date(), datetime.min.time())),
        'mean_visit_duration': 45,
        'visit_freq': 2 / 24
    }
