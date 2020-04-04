import argparse
import asyncio
import datetime
import logging
import random
import sys
from typing import Type

import schematics

from store import EventReaderWriter, EventType, Event, StrEnumType

logger = logging.getLogger("admin.py")


class AdminEventType(EventType):
    Create = "create"
    Extend = "extend"

    def to_cls(self) -> Type:
        if self == AdminEventType.Create:
            return CreateTicketEvent
        raise ValueError(f"Can't convert {self} to class")


class CreateTicketEvent(Event):
    type = StrEnumType(AdminEventType)
    user_name = schematics.types.StringType()
    deadline = schematics.types.DateTimeType(drop_tzinfo=True)


class ExtendTicketEvent(Event):
    type = StrEnumType(AdminEventType)
    new_deadline = schematics.types.DateTimeType(drop_tzinfo=True)


class AdminClient:
    def __init__(self):
        self.store = EventReaderWriter("tickets")

    async def info(self, no: str) -> dict:
        # Needs dependent type :(
        # noinspection PyTypeChecker
        create_event = await self.store.find_latest_event(AdminEventType.Create, str(no))
        res = create_event.to_primitive()
        return {k: v for k, v in res.items() if k in ['user_name', 'deadline']}

    async def create_ticket(self, user_name: str, day_duration: int) -> str:
        ticket_no = random.getrandbits(8)  # TODO: for debug
        t = datetime.datetime.now()
        create_event = CreateTicketEvent({  # TODO: make method
            'type': AdminEventType.Create.value,
            'object_name': str(ticket_no),
            'timestamp': t,
            'client_name': 'admin',
            'user_name': user_name,
            'deadline': t + datetime.timedelta(days=day_duration),
        })
        await self.store.push_event(create_event)
        return ticket_no

    async def extend_ticket(self, no: str, day_duration: int, *, from_date=None):
        # NOTE: We hope UI check that current season ticket is already expired.
        if from_date is not None:
            raise RuntimeError("from_data is not implement yet")
        t = datetime.datetime.now()
        create_event = ExtendTicketEvent({
            'type': AdminEventType.Extend.value,
            'object_name': no,
            'timestamp': t,
            'client_name': 'admin',
            'new_deadline': t + datetime.timedelta(days=day_duration)
        })
        await self.store.push_event(create_event)


async def main(args):
    admin = AdminClient()
    if args.command == 'info':
        info = await admin.info(args.no)
        print(info)
    elif args.command == 'create':
        no = await admin.create_ticket(args.name, args.hours)
        print(f"Ticket created with number: {no}")
    elif args.command == 'extend':
        await admin.extend_ticket(args.id, args.hours)
    else:
        raise RuntimeError("Unexpected sub-command")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser(description='Admin client')
    subparsers = parser.add_subparsers(dest='command', help="sub-command help")

    info_parser = subparsers.add_parser('info', help="info about season ticket")
    info_parser.add_argument('no', type=str, metavar="NO")

    create_parser = subparsers.add_parser('create', help="create new season ticket")
    create_parser.add_argument('name', type=str)
    create_parser.add_argument('-hs', '--hours', type=int, default=0, help="ticket duration in time")

    extend_parser = subparsers.add_parser('extend', help="extend season ticket")
    extend_parser.add_argument('id', type=str)
    extend_parser.add_argument('-hs', '--hours', type=int, required=True, help="ticket duration in time")

    asyncio.run(main(parser.parse_args()))
