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


async def init_indexes(collection):
    await collection.drop_indexes()
    await collection.create_index(
            [("secret_key", pymongo.HASHED)],
            sparse=True
            # expireAfterSeconds=secret_ttl
    )
    await collection.create_index(
            "secret_key",
            unique=True,
            expireAfterSeconds=secret_ttl
    )
    # await collection.create_index(
    #         "secret",
    # )


async def init_db(app):
    client = motor_asyncio.AsyncIOMotorClient(
            host=db_host, port=db_port,
            username=db_username,
            password=db_password
    )
    app["db"] = client[db_name]
    await client.drop_database(db_name)
    await init_indexes(app['db'][db_collection])


async def close_db(app):
    app['db'].client.close()
