# -*- coding: utf-8 -*-
"""Module with entrypoints for starting server

Examples:
    Server can be started via cli:
        $ python -m aiohttp.web app:init_app -H <host> -P <port> -U <socket>
    or via running this module with python directly:
        $ python -m app python -m src.app -P <port> -U <socket> --log-level <log-level>

"""

import asyncio
import logging
import argparse
from typing import Optional, List
from aiohttp import web

from .database import init_db, close_db
from .crypto import init_crypto
from .routes import urls


async def init_signals(app: web.Application):
    """Simple function for adding handlers to signals of application

    Args:
        app: Application to which handlers are added

    """
    app.on_startup.append(init_db)
    app.on_startup.append(init_crypto)

    app.on_cleanup.append(close_db)


async def init_app(argv: Optional[List[str]] = None) -> web.Application:
    """Main entrypoint function for starting server

    Args:
        argv: list with command line arguments.

    Returns:
        Application, that can be used immediately after returning

    """
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
