# -*- coding: utf-8 -*-
"""Module with helper functions for database initialization in aiohttp app.

"""
from aiohttp.abc import Application
from motor import motor_asyncio
import pymongo

from .settings import (
    secret_ttl,
    db_collection,
    db_name,
    db_password,
    db_username,
    db_host,
    db_port,
)


async def init_indexes(collection: motor_asyncio.AsyncIOMotorCollection):
    """Initializes indexes in MongoDB

    Args:
        collection: mongo collection in which indexes creates

    """

    await collection.drop_indexes()
    # Index for fast search secret_key
    await collection.create_index(
        [("secret_key", pymongo.HASHED)], sparse=True
    )
    # Max TTL for user's secret
    await collection.create_index(
        "secret_key", unique=True, expireAfterSeconds=secret_ttl
    )


async def init_db(app: Application):
    """Initializes database module in aiohttp application

    Must be handled via on_startup signal

    Args:
        app: initializing aiohttp application

    """

    client = motor_asyncio.AsyncIOMotorClient(
        host=db_host, port=db_port, username=db_username, password=db_password
    )
    app["db"] = client[db_name]
    await client.drop_database(db_name)
    await init_indexes(app["db"][db_collection])


async def close_db(app: Application):
    """Closes database connection.

    Must be handled via on_cleanup signal.

    Args:
        app: closing aiohttp application

    """

    app["db"].client.close()
