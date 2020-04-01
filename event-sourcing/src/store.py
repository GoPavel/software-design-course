import attr
from uuid import UUID
from typing import Optional, Any, Dict, Type
import enum

import pymongo
import schematics
import logging

import motor
import motor.motor_asyncio as aiomotor

logger = logging.getLogger(__name__)


# TODO: use automatic mongoId

class EventType(str, enum.Enum):
    pass

    def to_cls(self) -> Type:
        raise NotImplementedError


class StrEnumType(schematics.types.BaseType):
    def __init__(self, enum_cls: Type[enum.Enum], *args, **kwargs):
        if not issubclass(enum_cls, enum.Enum):
            raise TypeError("Expected enum class")
        if not issubclass(enum_cls, str):
            raise TypeError("Expected string enum class")

        super().__init__(*args, **kwargs)
        self.enum_cls = enum_cls

    def to_primitive(self, value, context=None):
        return value.value.encode()

    def to_native(self, value, context=None):
        return self.enum_cls(value.decode())


class Event(schematics.Model):
    type = StrEnumType(EventType)
    # revision = schematics.types.IntType()
    object_name = schematics.types.StringType()
    timestamp = schematics.types.TimestampType()
    client_name = schematics.types.StringType()


class MongoEventStoreBase:
    def __init__(self, collection_name: str):
        self.db_client = aiomotor.AsyncIOMotorClient('localhost', 27017)
        self._coll_name = collection_name
        self.coll = self.db_client[collection_name]

    @property
    def collection_name(self) -> str:
        return self._coll_name


class EventWriter(MongoEventStoreBase):

    def __init__(self, collection_name: str):
        super().__init__(collection_name)

    async def push_event(self, event: Event):
        logger.debug("Push event: %", event)
        await self.coll.insert_one(event.to_native())


class EventReader(MongoEventStoreBase):

    def __init__(self, collection_name: str):
        super().__init__(collection_name)

    async def find_latest_event(self, type: EventType, object_name: str) -> Event:
        doc = await self.coll.find({'type': type.value}) \
            .sort('timestamp', pymongo.DESCENDING) \
            .limit(1)
        return type.to_cls()(doc)


class EventReaderWriter(EventReader, EventWriter):
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
