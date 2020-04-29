from motor import motor_asyncio
import pymongo

from .settings import \
    secret_ttl, db_collection, db_name, db_password, db_username


async def init_indexes(collection):
    await collection.drop_indexes()
    await collection.create_index(
            [("secret_key", pymongo.HASHED)],
            # unique=True,
            sparse=True,
            expireAfterSeconds=secret_ttl
    )


async def init_db(app):
    client = motor_asyncio.AsyncIOMotorClient(
            host='localhost', port=27017,
            username=db_username,
            password=db_password
    )
    app["db"] = client[db_name]
    await init_indexes(app['db'][db_collection])


async def close_db(app):
    app['db'].client.close()
