from aiohttp import web
import json
import functools


class RequiredPostParameters:
    def __init__(self, param_list: list):
        self.params = param_list
    
    @property
    def explanation_body(self):
        return json.dumps({
            "Error": f"Required parameters: {', '.join(self.params)}."
        })
    
    def __call__(self, f: callable(web.Request)):
        
        @functools.wraps(f)
        async def check_params(request: web.Request):
            if request.body_exists:
                try:
                    body: dict = await request.json()
                except ValueError:
                    raise web.HTTPBadRequest(text=self.explanation_body)
            else:
                raise web.HTTPBadRequest(text=self.explanation_body)
    
            if "secret" not in body or "phrase" not in body:
                raise web.HTTPBadRequest(text=self.explanation_body)
            
            request.body = body
            return await f(request)
        
        return check_params
        
    
@RequiredPostParameters(["phrase", "secret"])
async def generate(request: web.Request):
    body = request.body
    secret_to_save = body["secret"]
    phrase = body["phrase"]
    raise web.HTTPOk
    # return web.Response(status=200)


async def get_secret(request: web.Request):
    
    raise web.HTTPOk


async def init_app(argv=None):
    app = web.Application()
    app.add_routes([
        web.post('/generate', generate),
        web.get('/secrets/{secret_key}', get_secret),
    ])
    return app
