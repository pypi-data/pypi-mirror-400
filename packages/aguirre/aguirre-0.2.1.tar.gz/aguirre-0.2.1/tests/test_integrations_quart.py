

import unittest


from quart import Quart
APP = Quart("demo")

import aguirre.integrations.quart as aguirre_quart
APP.register_blueprint(aguirre_quart.create_blueprint("tests/examples"),
                       url_prefix="/vendor")


class TestHeaders(unittest.IsolatedAsyncioTestCase):

    async def test_present(self):
        client = APP.test_client()
        x = await client.get("/vendor/vanjs-core@1.5.0/src/van.js")
        self.assertEqual(x.status_code, 200)
        self.assertIn("Cache-Control", x.headers)
        self.assertIn("immutable", x.headers["Cache-Control"])

    async def test_absent(self):
        client = APP.test_client()
        x = await client.get("/vendor/vanjs-core@1.5.0/src/missing.js")
        self.assertEqual(x.status_code, 404)
        # FIXME... what caching *do* we want for failures?
