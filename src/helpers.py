# -*- coding: utf-8 -*-
"""Module with general purpose helper functions

"""

from typing import Iterable, Mapping, Union, Callable
from datetime import datetime, timedelta
import functools
import json

from aiohttp import web

from .settings import secret_ttl


class RequiredPostParameters:
    """Decorator for web handlers, that checks request body before handler call

    Checks, whether request body is valid json, containing defined
    toplevel parameters. If request is not valid, returns 400 response
    without handler call.

    Places "body" param in request.

    Attributes:
        params: parameters to check.

    """

    def __init__(self, param_list: Iterable[str]):
        self.params = param_list

    @property
    def explanation_body(self) -> Mapping[str, str]:
        """Helper property to get dict with "Error" key

        """

        return {"Error": f"Required parameters: {', '.join(self.params)}."}

    def __call__(
        self, f: Callable[[web.Request], web.Response]
    ) -> Callable[[web.Request], web.Response]:
        @functools.wraps(f)
        async def check_params(request: web.Request) -> web.Response:
            if request.body_exists:
                try:
                    body = await request.json()
                except ValueError:
                    return web.json_response(
                        self.explanation_body, status=400
                    )
                else:
                    for param in self.params:
                        if param not in body:
                            return web.json_response(
                                self.explanation_body, status=400
                            )
            else:
                return web.json_response(self.explanation_body, status=400)

            request["body"] = body
            # noinspection PyUnresolvedReferences
            return await f(request)

        # noinspection PyTypeChecker
        return check_params  # type: Callable[[web.Request], web.Response]


async def parse_ttl(ttl: Mapping[str, int]) -> datetime:
    """Parses ttl dict, passed on "/generate" uri.

    Dict must contain one of the "days", "hours" or "minutes" parameters.
    Otherwise raises HTTPBadRequest error.

    If gotten parameters are negative, they are considered as 0.

    Result ttl as 0 seconds is considered as valid. In this case secret
    will not be returned.

    If result ttl is more than ttl set by database index, then secret will be
    simply removed before user expected date.

    Args:
        ttl: Raw dict from request.

    Returns:
        Datetime when secret is expires.

    Raises:
        HTTPBadRequest: returns 400 to user, when he/she passes invalid ttl.

    """

    now = datetime.now()

    if not ("days" in ttl or "hours" in ttl or "minutes" in ttl):
        raise web.HTTPBadRequest(
            text=json.dumps(
                {
                    "Error": "Provide at least one of next "
                    'parameters in object "ttl":\n'
                    '"days", "hours", "minutes"'
                }
            )
        )

    days = ttl.get("days", 0)
    hours = ttl.get("hours", 0)
    minutes = ttl.get("minutes", 0)
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    delta = max(delta, timedelta(0))
    return now + delta


async def is_expired(
    secret_document: Union[None, Mapping[str, Union[bytes, datetime, str]]]
) -> bool:
    """Parses document from mongo, and checks if secret expired.

    Args:
        secret_document: mongo document, returned for secret_key that
            user passed via request.

    Returns:
        If document is None, then it was deleted by ttl index,
        hence returns False.

        If field "expires_at" is not exists in document, then its expiring
        handled by only ttl index,
        hence returns True.

        Otherwise, returns if current datetime > expiring datetime

    """

    if secret_document is None:
        return True
    elif "expires_at" not in secret_document:
        return False
    else:
        print(datetime.now().isoformat())
        return secret_document["expires_at"] < datetime.now()
