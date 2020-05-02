from aiohttp import web

from . import web_handlers


urls = [
    web.post("/generate", web_handlers.generate),
    web.post("/secrets/{secret_key}", web_handlers.get_secret),
]
