import argparse
import asyncio
import logging
import random
import sys
from datetime import datetime
from typing import Type

import schematics

from manager_admin import AdminEventType
from store import EventReaderWriter, EventType, Event, StrEnumType

logger = logging.getLogger("turnstile")


class TurnstileEventType(EventType):
    CameIn = 'came_in'
    Leave = 'leave'

    def to_cls(self) -> Type:
        # if self ==
        pass


class CameInEvent(Event):
    type = StrEnumType(TurnstileEventType)


class LeaveEvent(Event):
    type = StrEnumType(TurnstileEventType)


class TurnstileClient:

    def __init__(self, store: EventReaderWriter):
        self.store = store

    async def _check_deadline(self, no: str, now: datetime) -> bool:
        extend_event = await self.store.find_latest_event(AdminEventType.Extend, no)
        if extend_event:
            t = extend_event.deadline
        else:
            create_event = await self.store.find_latest_event(AdminEventType.Create, no)
            if not create_event:
                raise RuntimeError(f"Can't find ticket with no {no}")
            t = create_event.deadline
        return now < t

    async def came_in(self, no: str) -> bool:
        t = datetime.now()
        if not await self._check_deadline(no, t):
            return False
        event = LeaveEvent({
            'type': TurnstileEventType.CameIn,
            'object_name': no,
            'timestamp': t,
            'client_name': 'turnstile'
        })
        await self.store.push_event(event)
        return True

    async def leave(self, no: str):
        t = datetime.now()
        event = LeaveEvent({
            'type': TurnstileEventType.Leave,
            'object_name': no,
            'timestamp': t,
            'client_name': 'turnstile'
        })
        await self.store.push_event(event)


async def main(args):
    store = EventReaderWriter('tickets')
    turnstile = TurnstileClient(store)
    if getattr(args, 'in'):
        succ = await turnstile.came_in(args.no)
        print("OK" if succ else "FAIL")
    elif args.out:
        await turnstile.leave(args.no)
    else:
        raise RuntimeError(f'Wrong arguments: {args}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser(description='turnstile client')
    parser.add_argument('no', type=str, metavar='NO', help='number of ticket')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--in', action='store_true', help='client came in')
    g.add_argument('--out', action='store_true', help='client leaved')

    asyncio.run(main(parser.parse_args()))
