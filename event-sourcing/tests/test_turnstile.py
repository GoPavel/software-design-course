from datetime import datetime, timedelta

import pytest
from asynctest.mock import CoroutineMock, Mock

from manager_admin import CreateTicketEvent, AdminEventType, ExtendTicketEvent
from store import EventReaderWriter
from turnstile import TurnstileService, TurnstileEventType


@pytest.mark.asyncio
async def test_check_deadline_1():
    t = datetime.fromtimestamp(1)
    dt = timedelta(days=2)
    create_event = CreateTicketEvent({
        'type': 'create',
        'object_name': '42',
        'timestamp': t,
        'client_name': 'test_admin',
        'user_name': 'Bob',
        'deadline': t + dt
    })
    store = Mock(EventReaderWriter)
    store.find_latest_event = CoroutineMock(side_effect=[None, create_event])
    assert await TurnstileService(store)._check_deadline('42', t + timedelta(days=1))
    store.find_latest_event.assert_awaited_with(AdminEventType.Create, '42')

    store.find_latest_event = CoroutineMock(side_effect=[None, create_event])
    assert not await TurnstileService(store)._check_deadline('42', t + timedelta(days=3))
    store.find_latest_event.assert_awaited_with(AdminEventType.Create, '42')


@pytest.mark.asyncio
async def test_check_deadline_2():
    t = datetime.fromtimestamp(1)
    dt = timedelta(days=2)
    create_event = ExtendTicketEvent({
        'type': 'create',
        'object_name': '42',
        'timestamp': t,
        'client_name': 'test_admin',
        'deadline': t + dt
    })
    store = Mock(EventReaderWriter)
    store.find_latest_event = CoroutineMock(return_value=create_event)
    assert await TurnstileService(store)._check_deadline('42', t + timedelta(days=1))
    store.find_latest_event.assert_awaited_once_with(AdminEventType.Extend, '42')

    store.find_latest_event = CoroutineMock(return_value=create_event)
    assert not await TurnstileService(store)._check_deadline('42', t + timedelta(days=3))
    store.find_latest_event.assert_awaited_once_with(AdminEventType.Extend, '42')


@pytest.mark.asyncio
async def test_came_in_1():
    store = Mock(EventReaderWriter)
    store.push_event = CoroutineMock()
    turnstile = TurnstileService(store)
    turnstile._check_deadline = CoroutineMock(return_value=False)

    assert not await turnstile.came_in('42')
    turnstile._check_deadline.assert_awaited_once()
    assert turnstile._check_deadline.await_args[0][0] == '42'
    store.push_event.assert_not_awaited()


@pytest.mark.asyncio
async def test_came_in_2():
    store = Mock(EventReaderWriter)
    store.push_event = CoroutineMock()
    turnstile = TurnstileService(store)
    turnstile._check_deadline = CoroutineMock(return_value=True)

    assert await turnstile.came_in('42')
    turnstile._check_deadline.assert_awaited_once()
    assert turnstile._check_deadline.await_args[0][0] == '42'
    store.push_event.assert_awaited_once()
    event = store.push_event.await_args[0][0]
    assert event.type == TurnstileEventType.CameIn
    assert event.object_name == '42'


@pytest.mark.asyncio
async def test_leave():
    store = Mock(EventReaderWriter)
    store.push_event = CoroutineMock()
    turnstile = TurnstileService(store)

    await turnstile.leave('42')
    store.push_event.assert_awaited_once()
    event = store.push_event.await_args[0][0]
    assert event.type == TurnstileEventType.Leave
    assert event.object_name == '42'

