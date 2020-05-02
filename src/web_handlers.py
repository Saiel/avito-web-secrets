from aiohttp import web
import json

from .helpers import RequiredPostParameters, parse_ttl, is_expired
from .settings import db_collection


@RequiredPostParameters(["phrase", "secret"])
async def generate(request: web.Request) -> web.Response:
    body = request["body"]
    raw_secret = body["secret"]
    raw_phrase = body["phrase"]

    raw_ttl = body.get("ttl", None)
    expires_at = None
    if raw_ttl:
        expires_at = await parse_ttl(raw_ttl)

    cr = request.app["crypto"]

    secret_to_save = cr.encrypt(raw_secret)
    phrase_to_save = cr.encrypt(raw_phrase)
    key = cr.generate_key()

    doc_with_secret = {
        "secret": secret_to_save,
        "phrase": phrase_to_save,
        "secret_key": key,
    }
    if expires_at:
        doc_with_secret["expires_at"] = expires_at

    request.app["db"][db_collection].insert_one(doc_with_secret)

    response_body = {
        "secret_key": key,
    }

    return web.json_response(response_body, status=201)


@RequiredPostParameters(["phrase"])
async def get_secret(request: web.Request) -> web.Response:
    collection = request.app["db"][db_collection]

    body = request["body"]
    given_phrase = body["phrase"]

    secret_key = request.match_info["secret_key"]

    fil = {"secret_key": secret_key}
    saved_secret = await collection.find_one(fil)

    if await is_expired(saved_secret):
        return web.json_response({"Error": "Key not found"}, status=404)

    control_phrase = request.app["crypto"].decrypt(saved_secret["phrase"])
    if given_phrase != control_phrase:
        return web.json_response({"Error": "Incorrect phrase"}, status=403)

    secret = request.app["crypto"].decrypt(saved_secret["secret"])

    await collection.delete_one(fil)

    return web.json_response({"secret": secret}, status=200)
