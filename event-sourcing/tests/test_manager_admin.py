from datetime import datetime, timedelta

import pytest
from asynctest.mock import CoroutineMock, Mock

from manager_admin import CreateTicketEvent, AdminService, AdminEventType
from store import EventReaderWriter


@pytest.mark.asyncio
async def test_info():
    t = datetime.fromtimestamp(1)
    dt = timedelta(days=1)
    create_event = CreateTicketEvent({
        'type': 'create',
        'object_name': '42',
        'timestamp': t,
        'client_name': 'test_admin',
        'user_name': 'Bob',
        'deadline': t + dt
    })
    store = Mock(EventReaderWriter)
    store.find_latest_event = CoroutineMock(return_value=create_event)
    res = await AdminService(store).info('42')
    assert res == {'user_name': 'Bob', 'deadline': str(t + dt)}
    store.find_latest_event.assert_awaited_once_with(AdminEventType.Create, '42')


@pytest.mark.asyncio
async def test_create_ticket():
    store = Mock(EventReaderWriter)
    store.push_event = CoroutineMock()
    await AdminService(store).create_ticket('Bob', 1)
    store.push_event.assert_awaited_once()
    event = store.push_event.await_args[0][0] # TODO
    assert event.user_name == 'Bob'
    assert event.type == AdminEventType.Create
    assert event.timestamp is not None


@pytest.mark.asyncio
async def test_extend_ticket():
    store = Mock(EventReaderWriter)
    store.push_event = CoroutineMock()
    await AdminService(store).extend_ticket('42', 1)
    store.push_event.assert_awaited_once()
    event = store.push_event.await_args[0][0]
    assert event.type == AdminEventType.Extend
    assert event.object_name == '42'
    assert event.timestamp is not None

