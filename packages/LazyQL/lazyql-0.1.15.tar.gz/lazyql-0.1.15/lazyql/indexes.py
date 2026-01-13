import logging
from typing import List, Type

import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import BaseDBModel

logger = logging.getLogger(__name__)


async def ensure_unique_index(
    db: AsyncIOMotorDatabase, collection_name: str, field: str
):
    """
    Ensure a unique index on a specified field,
    excluding soft-deleted documents.
    """
    collection = db[collection_name]
    index_name = f"unique_active_{field}"

    try:
        await collection.create_index(
            [(field, pymongo.ASCENDING)],
            name=index_name,
            unique=True,
            partialFilterExpression={"deleted_at": None},
            background=True,
        )
    except Exception as e:
        logger.warning(
            f"Could not create unique index on "
            f"'{collection_name}.{field}': {e}",
            exc_info=True,
        )


async def _sync_model_indexes(
    db: AsyncIOMotorDatabase, model: Type[BaseDBModel]
):
    """
    Sync unique indexes for a single model based
    on its SlothMeta configuration.
    """
    meta = getattr(model, "SlothMeta", None)
    if not meta:
        return

    collection_name = getattr(meta, "collection", None)
    if not collection_name:
        collection_name = model.__name__.lower() + "s"

    unique_fields = getattr(meta, "unique_fields", [])
    if not unique_fields:
        return

    for field in unique_fields:
        try:
            await ensure_unique_index(db, collection_name, field)
        except Exception as e:
            logger.error(
                f"Error ensuring index for {collection_name}.{field}: {e}",
                exc_info=True,
            )


async def sync_indexes(
    db: AsyncIOMotorDatabase, models: List[Type[BaseDBModel]]
):
    """
    Sync unique indexes for all models based on their SlothMeta configuration.
    """
    for model in models:
        await _sync_model_indexes(db, model)
