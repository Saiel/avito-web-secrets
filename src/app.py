from aiohttp import web

from .database import init_db, close_db
from .routes import urls


async def init_signals(app: web.Application):
    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)


async def init_app(argv=None):
    app = web.Application()
    
    await init_signals(app)
    app.add_routes(urls)
    
    return app
