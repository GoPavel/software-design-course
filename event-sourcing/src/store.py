import enum
import logging
from datetime import datetime
from typing import Optional, Dict, Type

import motor.motor_asyncio as aiomotor
import pymongo
import schematics

from models import ConstStringType

logger = logging.getLogger(__name__)


# TODO: use automatic mongoId

class EventType(str, enum.Enum):
    pass


class MongoObjectIdType(schematics.models.BaseType):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # TODO


class Event(schematics.Model):
    # _id = MongoObjectIdType()
    type = ConstStringType("")
    # revision = schematics.types.IntType()
    object_name = schematics.types.StringType()
    timestamp = schematics.types.TimestampType(drop_tzinfo=True)
    client_name = schematics.types.StringType()

    def validate_type(self, value, context=None):
        if not value['type']:
            raise schematics.types.ValidationError('Empty type')


EVENT_TYPE_TO_EVENT_CLASS: Dict[str, Type[Event]] = {}


class MongoEventStoreBase:
    def __init__(self, db_name: str):
        self._mongo_client = aiomotor.AsyncIOMotorClient('localhost', 27017)
        self._db = self._mongo_client[db_name]
        self._coll = self._db['events']


class EventWriter(MongoEventStoreBase):
    def __init__(self, db_name: str):
        super().__init__(db_name)

    async def push_event(self, event: Event):
        logger.debug("Push event: %s", event.to_primitive())
        await self._coll.insert_one(event.to_primitive())


class EventReader(MongoEventStoreBase):

    def __init__(self, db_name: str):
        super().__init__(db_name)

    async def find_latest_event(self, type: EventType, object_name: str) -> Optional[Event]:
        logger.debug("find latest event with type \"%s\", for object %s", type.value, object_name)
        cursor = self._coll \
            .find({'type': type.value, 'object_name': object_name},
                  projection={'_id': False}) \
            .sort('timestamp', pymongo.DESCENDING)
        async for doc in cursor:
            if not doc:
                raise RuntimeError(f"Can't find any \"{type.value}\" event for object \"{object_name}\"")
            event = EVENT_TYPE_TO_EVENT_CLASS[type.value](doc)
            print(event.to_primitive())
            event.validate()
            return event
        return None

    async def find_all(self, *, from_time: datetime, to_time: datetime):
        cursor = self._coll \
            .find(
            {'$and': [
                {'timestamp': {'$gte': from_time.timestamp()}},
                {'timestamp': {'$lte': to_time.timestamp()}},
            ]},
            projection={'_id': False}) \
            .sort('timestamp')
        async for doc in cursor:
            if doc['type'] not in EVENT_TYPE_TO_EVENT_CLASS:
                logger.warning(f"Unknown type of event: {doc['type']}")
                continue
            event = EVENT_TYPE_TO_EVENT_CLASS[doc['type']](doc)
            event.validate()
            yield event


class EventReaderWriter(EventReader, EventWriter):
    def __init__(self, db_name: str):
        super().__init__(db_name)
