from datetime import datetime, timedelta
from typing import Optional, Union, Mapping

from aiohttp import test_utils as tu
from aiohttp.web import Application

from .app import init_app, web
from .settings import db_collection
from .helpers import RequiredPostParameters, parse_ttl, is_expired


class HandlersTestCase(tu.AioHTTPTestCase):
    client: tu.TestClient
    server: tu.TestServer

    async def get_application(self) -> Application:
        return await init_app()

    async def _add_secret(
            self,
            phrase: str,
            secret: str,
            ttl: Optional[Mapping[str, Union[float, int]]] = None
    ):
        payload = {
            "phrase": phrase,
            "secret": secret,
        }
        if ttl:
            payload["ttl"] = ttl
        return await self.client.post("/generate", json=payload)

    async def _get_new_key(
            self,
            phrase: str,
            secret: str,
            ttl: Optional[Mapping[str, Union[float, int]]] = None
    ):
        resp = await self._add_secret(phrase, secret, ttl)
        self.assertEqual(resp.status, 201)

        body = await resp.json()
        self.assertIn("secret_key", body)

        return body["secret_key"]

    @tu.unittest_run_loop
    async def test_normal_workflow(self):
        phrase = "test phrase"
        secret = "test"

        key = await self._get_new_key(phrase, secret)

        payload = {
            "phrase": phrase
        }

        resp = await self.client.post(f"/secrets/{key}", json=payload)
        self.assertEqual(resp.status, 200)

        body = await resp.json()
        self.assertIn("secret", body)

        resp_secret = body["secret"]
        self.assertEqual(resp_secret, secret)

    @tu.unittest_run_loop
    async def test_wrong_phrase(self):
        phrase = "test phrase"
        secret = "test"

        key = await self._get_new_key(phrase, secret)

        payload = {
            "phrase": "wrong phrase"
        }

        resp = await self.client.post(f"/secrets/{key}", json=payload)
        self.assertEqual(resp.status, 403)

        body = await resp.json()
        self.assertIn("Error", body)

        error_message = body["Error"]
        self.assertEqual(error_message, "Incorrect phrase")

    @tu.unittest_run_loop
    async def test_key_not_found(self):
        payload = {
            "phrase": "some phrase"
        }

        resp = await self.client.post("/secrets/wrong_key", json=payload)
        self.assertEqual(resp.status, 404)

        body = await resp.json()
        self.assertIn("Error", body)

        error_message = body["Error"]
        self.assertEqual(error_message, "Key not found")

    @tu.unittest_run_loop
    async def test_normal_ttl(self):
        phrase = "test phrase"
        secret = "test"
        ttl = {"days": 1, "hours": 2, "minutes": 3}

        key = await self._get_new_key(phrase, secret, ttl)

        fil = {
            "secret_key": key
        }
        saved_secret = await self.app["db"][db_collection].find_one_and_delete(fil)
        self.assertIn("expires_at", saved_secret)


class HelpersTestCase(tu.AioHTTPTestCase):
    required_params = ["test1", "test2"]
    
    async def get_application(self) -> Application:
        @RequiredPostParameters(self.required_params)
        async def test_handler(request):
            return web.Response()
        
        app = web.Application()
        app.router.add_post("/", test_handler)
        return app
    
    def test_explanation_body(self, body=None):
        if body is None:
            body = RequiredPostParameters(self.required_params).explanation_body

        self.assertDictEqual(body, {
            "Error": f"Required parameters: {', '.join(self.required_params)}."
        })
    
    @tu.unittest_run_loop
    async def test_empty_body(self):
        resp = await self.client.post("/")
        self.assertEqual(resp.status, 400)
        self.test_explanation_body(await resp.json())
    
    @tu.unittest_run_loop
    async def test_body_not_json(self):
        resp = await self.client.post("/", data="some body")  # once told me...
        self.assertEqual(resp.status, 400)
        self.test_explanation_body(await resp.json())
    
    @tu.unittest_run_loop
    async def test_wrong_params(self):
        resp = await self.client.post("/", json={"wrong param": "test"})
        self.assertEqual(resp.status, 400)
        self.test_explanation_body(await resp.json())
    
    @tu.unittest_run_loop
    async def test_normal_ttl(self):
        days = 1
        now = datetime.now()
        ttl = now + timedelta(days=days) 
        
        test_ttl = await parse_ttl({"days": days})
        
        self.assertAlmostEqual(test_ttl, ttl, delta=timedelta(seconds=5))
    
    @tu.unittest_run_loop
    async def test_bad_ttl(self):
        with self.assertRaises(web.HTTPBadRequest):
            await parse_ttl({
                "bad param": 0,
                "and none of the 'days', 'hours' or 'minutes'": 1,
            })
    
    @tu.unittest_run_loop
    async def test_none_in_is_expired(self):
        self.assertTrue(await is_expired(None))

    @tu.unittest_run_loop
    async def test_lack_of_expired_at(self):
        self.assertFalse(await is_expired({"some_field": b"encrypted str"}))
    
    @tu.unittest_run_loop
    async def test_normal_is_expired(self):
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        yesterday = now - timedelta(days=1)
        
        self.assertFalse(await is_expired({"expires_at": tomorrow}))
        self.assertTrue(await is_expired({"expires_at": yesterday}))
