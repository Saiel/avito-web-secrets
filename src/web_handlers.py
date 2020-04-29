from aiohttp import web

from .helpers import RequiredPostParameters


@RequiredPostParameters(["phrase", "secret"])
async def generate(request: web.Request):
    body = request["body"]
    secret_to_save = body["secret"]
    phrase = body["phrase"]
    
    raise web.HTTPOk
    # return web.Response(status=200)


@RequiredPostParameters(["phrase"])
async def get_secret(request: web.Request):
    raise web.HTTPOk
