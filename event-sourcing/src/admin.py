import argparse
import asyncio
import logging
from typing import Type

import schematics

from store import EventReaderWriter, EventType, Event

logger = logging.getLogger("admin.py")


class AdminEventType(EventType):
    Create = "create"
    Extend = "extend"

    def to_cls(self) -> Type:
        if self == AdminEventType.Create:
            return CreateTicketEvent


class CreateTicketEvent(Event):
    user_name = schematics.types.StringType()
    deadline = schematics.types.DateTimeType()


class AdminClient:
    def __init__(self):
        self.store = EventReaderWriter("tickets")

    async def info(self, no: int) -> dict:
        # Needs dependent type :(
        # noinspection PyTypeChecker
        create_event: CreateTicketEvent = await self.store.find_latest_event(AdminEventType.Create, str(no))
        return create_event.to_primitive()

    async def create_ticket(self) -> int:
        create_event = CreateTicketEvent({}) # TODO

async def main(args):
    admin = AdminClient()
    if args.subparser_name == 'info':
        await admin.info(args.no)
    elif args.subparser_name == 'create':
        pass
    elif args.subparser_name == 'extend':
        pass
    else:
        raise RuntimeError("Unexpected sub-command")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin client")
    subparsers = parser.add_subparsers(help="sub-command help")

    info_parser = subparsers.add_parser("info", help="info about season ticket")
    info_parser.add_argument('no', type=int, metavar="NO")

    create_parser = subparsers.add_parser("create", help="create new season ticket")
    # TODO

    extend_parser = subparsers.add_parser("extend", help="extend season ticket")
    # TODO

    asyncio.run(main(parser.parse_args()))
