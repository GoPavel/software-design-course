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
        return value.value

    def to_native(self, value, context=None):
        if isinstance(value, bytes):
            value = value.decode()
        return self.enum_cls(value)


class MongoObjectIdType(schematics.models.BaseType):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # TODO


class Event(schematics.Model):
    # _id = MongoObjectIdType()
    type = StrEnumType(EventType)
    # revision = schematics.types.IntType()
    object_name = schematics.types.StringType()
    timestamp = schematics.types.TimestampType(drop_tzinfo=True)
    client_name = schematics.types.StringType()

    def validate_call_me(self, value):
        del value['_id']


class MongoEventStoreBase:
    def __init__(self, collection_name: str):
        self._mongo_client = aiomotor.AsyncIOMotorClient('localhost', 27017)
        self._db = self._mongo_client['event-source-hw']
        self._coll = self._db[collection_name]
        self._coll_name = collection_name

    @property
    def db_client(self) -> aiomotor.AsyncIOMotorDatabase:
        return self._db

    @property
    def collection(self) -> aiomotor.AsyncIOMotorCollection:
        return self._coll_name


class EventWriter(MongoEventStoreBase):
    def __init__(self, collection_name: str):
        super().__init__(collection_name)

    async def push_event(self, event: Event):
        logger.debug("Push event: %s", event.to_primitive())
        await self._coll.insert_one(event.to_primitive())


class EventReader(MongoEventStoreBase):

    def __init__(self, collection_name: str):
        super().__init__(collection_name)

    async def find_latest_event(self, type: EventType, object_name: str) -> Optional[Event]:
        logger.debug("find latest event with type \"%s\", for object %s", type.value, object_name)
        cursor = self._coll \
            .find({'type': type.value}) \
            .sort('timestamp', pymongo.DESCENDING)
        async for doc in cursor:
            if not doc:
                raise RuntimeError(f"Can't find any \"{type.value}\" event for object \"{object_name}\"")
            return type.to_cls()(doc)
        return None


class EventReaderWriter(EventReader, EventWriter):
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
