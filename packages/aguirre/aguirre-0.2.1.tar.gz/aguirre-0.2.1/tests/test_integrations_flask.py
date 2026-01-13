

import unittest


from flask import Flask
APP = Flask("demo")

import aguirre.integrations.flask as aguirre_flask
APP.register_blueprint(aguirre_flask.create_blueprint("tests/examples"),
                       url_prefix="/vendor")


class TestHeaders(unittest.TestCase):

    def test_present(self):
        client = APP.test_client()
        x = client.get("/vendor/vanjs-core@1.5.0/src/van.js")
        self.assertTrue(x.status.startswith("200 "))
        self.assertIn("Cache-Control", x.headers)
        self.assertIn("immutable", x.headers["Cache-Control"])

    def test_absent(self):
        client = APP.test_client()
        x = client.get("/vendor/vanjs-core@1.5.0/src/missing.js")
        self.assertTrue(x.status.startswith("404 "))
        # FIXME... what caching *do* we want for failures?
