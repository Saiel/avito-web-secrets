from typing import Iterable, Mapping, Union
from datetime import datetime, timedelta
import functools
import json

from aiohttp import web

from .settings import secret_ttl


class RequiredPostParameters:
    def __init__(self, param_list: Iterable[str]):
        self.params = param_list
    
    @property
    def explanation_body(self):
        return {"Error": f"Required parameters: {', '.join(self.params)}."}
    
    def __call__(self, f: callable(web.Request)):
        
        @functools.wraps(f)
        async def check_params(request: web.Request) -> web.Response:
            if request.body_exists:
                try:
                    body: dict = await request.json()
                except ValueError:
                    return web.json_response(self.explanation_body, status=400)
                else:
                    if "secret" not in body or "phrase" not in body:
                        return web.json_response(self.explanation_body, status=400)
            else:
                return web.json_response(self.explanation_body, status=400)
            
            request["body"] = body
            return await f(request)
        
        return check_params


async def parse_ttl(ttl: Mapping[str, int]) -> datetime:
    now = datetime.now()
    
    if not (
            "days" in ttl or
            "hours" in ttl or
            "minutes" in ttl
    ):
        raise web.HTTPBadRequest(
                text=json.dumps({
                    "Error": "Provide at least one of next "
                             "parameters in object \"ttl\":\n"
                             "\"days\", \"hours\", \"minutes\""
                })
        )
    
    days = ttl.get("days", 0)
    hours = ttl.get("hours", 0)
    minutes = ttl.get("minutes", 0)
    delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes
    )
    delta = min(delta, timedelta(seconds=secret_ttl))
    delta = max(delta, timedelta(0))
    return now + delta


async def is_expired(
        secret_document: Union[None, Mapping[str, Union[bytes, datetime, str]]]
) -> bool:
    if secret_document is None:
        return True
    elif "expires_at" not in secret_document:
        return False
    else:
        return secret_document["expires_at"] > datetime.now()
