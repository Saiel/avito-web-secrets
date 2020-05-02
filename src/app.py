import asyncio
import logging
import argparse
from typing import Optional
from aiohttp import web

from .database import init_db, close_db
from .crypto import init_crypto
from .routes import urls


async def init_signals(app: web.Application):
    app.on_startup.append(init_db)
    app.on_startup.append(init_crypto)

    app.on_cleanup.append(close_db)


async def init_app(argv: Optional[list] = None):
    app = web.Application()

    await init_signals(app)
    app.add_routes(urls)

    return app


_parser = argparse.ArgumentParser()
_parser.add_argument("-P", "--port", dest="port")
_parser.add_argument("-U", "--socket", dest="socket")
_parser.add_argument(
    "--log-level",
    dest="log_level",
    choices=(
        "CRITICAL",
        "FATAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG",
        "NOTSET",
    ),
    default=logging.DEBUG,
)

if __name__ == "__main__":

    args = _parser.parse_args()

    logging.basicConfig(level=args.log_level)
    loop = asyncio.get_event_loop()
    try:
        web.run_app(
            loop.run_until_complete(init_app()),
            host="0.0.0.0",
            port=args.port,
            path=args.socket,
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
