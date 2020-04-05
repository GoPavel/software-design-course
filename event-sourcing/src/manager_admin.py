import argparse
import asyncio
import logging
import random
import sys
from datetime import datetime, timedelta

import schematics

from models import ConstStringType
from store import EventReaderWriter, EventType, Event, EVENT_TYPE_TO_EVENT_CLASS

logger = logging.getLogger("manager_admin")


class AdminEventType(EventType):
    Create = "create"
    Extend = "extend"


class CreateTicketEvent(Event):
    type = ConstStringType(AdminEventType.Create)
    user_name = schematics.types.StringType()
    deadline = schematics.types.DateTimeType(serialized_format='%Y-%m-%d %H:%M:%S', drop_tzinfo=True)


class ExtendTicketEvent(Event):
    type = ConstStringType(AdminEventType.Extend)
    deadline = schematics.types.DateTimeType(serialized_format='%Y-%m-%d %H:%M:%S', drop_tzinfo=True)


EVENT_TYPE_TO_EVENT_CLASS[AdminEventType.Create] = CreateTicketEvent  # TODO add subclass_hook for it
EVENT_TYPE_TO_EVENT_CLASS[AdminEventType.Extend] = ExtendTicketEvent


class AdminService:
    def __init__(self, store: EventReaderWriter):
        self.store = store

    async def info(self, no: str) -> dict:
        # Needs dependent type :(
        # noinspection PyTypeChecker
        create_event = await self.store.find_latest_event(AdminEventType.Create, str(no))
        if not create_event:
            raise RuntimeError(f"Can't find ticket with no {no}")
        res = create_event.to_primitive()
        return {k: v for k, v in res.items() if k in ['user_name', 'deadline']}

    async def create_ticket(self, user_name: str, day_duration: int) -> str:
        ticket_no = random.getrandbits(8)  # TODO: for debug
        t = datetime.now()
        create_event = CreateTicketEvent({  # TODO: make method
            'type': AdminEventType.Create.value,
            'object_name': str(ticket_no),
            'timestamp': t,
            'client_name': 'admin',  # TODO: capture to EventStore class
            'user_name': user_name,
            'deadline': t + timedelta(days=day_duration),
        })
        await self.store.push_event(create_event)
        return ticket_no

    async def extend_ticket(self, no: str, day_duration: int, *, from_date=None):
        # NOTE: We hope UI check that current season ticket is already expired.
        if from_date is not None:
            raise RuntimeError("from_data is not implement yet")
        t = datetime.now()
        create_event = ExtendTicketEvent({
            'type': AdminEventType.Extend.value,
            'object_name': no,
            'timestamp': t,
            'client_name': 'admin',
            'deadline': t + timedelta(days=day_duration)
        })
        await self.store.push_event(create_event)


async def main(args):
    store = EventReaderWriter(db_name='event-source-hw')
    admin = AdminService(store)
    if args.command == 'info':
        info = await admin.info(args.no)
        print(info)
    elif args.command == 'create':
        no = await admin.create_ticket(args.name, args.days)
        print(f"Ticket created with number: {no}")
    elif args.command == 'extend':
        await admin.extend_ticket(args.id, args.days)
    else:
        raise RuntimeError("Unexpected sub-command")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser(description='Manager admin client')
    subparsers = parser.add_subparsers(dest='command', help="sub-command help")

    info_parser = subparsers.add_parser('info', help="info about season ticket")
    info_parser.add_argument('no', type=str, metavar="NO")

    create_parser = subparsers.add_parser('create', help="create new season ticket")
    create_parser.add_argument('name', type=str)
    create_parser.add_argument('-d', '--days', type=int, default=0, help="ticket duration")

    extend_parser = subparsers.add_parser('extend', help="extend season ticket")
    extend_parser.add_argument('id', type=str)
    extend_parser.add_argument('-d', '--days', type=int, required=True, help="ticket duration")

    asyncio.run(main(parser.parse_args()))
