from typing import Iterable
import functools
import json

from aiohttp import web


class RequiredPostParameters:
    def __init__(self, param_list: Iterable[str]):
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
                    if "secret" not in body or "phrase" not in body:
                        raise web.HTTPBadRequest(text=self.explanation_body)
            else:
                raise web.HTTPBadRequest(text=self.explanation_body)
            
            request["body"] = body
            return await f(request)
        
        return check_params
