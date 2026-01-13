

import datetime
from os.path import dirname, join
import unittest

from aguirre import util


def example_dir():
    return join(dirname(__file__), "examples")


class TestHighLevelLoading(unittest.TestCase):

    def test_loading_from_a_tarball(self):
        x = util.load_from_package(example_dir(), "vanjs-core", "1.5.0", "src/van.js")
        self.assertEqual(len(x), 4917)

    def test_missing_from_a_tarball(self):
        x = util.load_from_package(example_dir(), "vanjs-core", "1.5.0", "other.js")
        self.assertIsNone(x)

    def test_from_a_package_that_doesnt_exist(self):
        x = util.load_from_package(example_dir(), "vanjs-core", "9.9.9", "src/van.js")
        self.assertIsNone(x)


class TestTarballLowLevelAccess(unittest.TestCase):

    def setUp(self):
        self.tarpath = join(example_dir(), "vanjs-core-1.5.0.tgz")
        self.badpath = join(example_dir(), "not-an-archive.txt")

    def test_loading_a_good_file(self):
        result = util.load_from_tarball(self.tarpath, "package/src/van.js")
        self.assertEqual(len(result), 4917)

    def test_failing_on_a_bad_file(self):
        with self.assertRaises(KeyError):
            util.load_from_tarball(self.tarpath, "src/van.js")

    def test_failing_on_a_bad_archive(self):
        with self.assertRaises(Exception):
            util.load_from_tarball(self.badpath, "package/src/van.js")


class TestMimeTypes(unittest.TestCase):

    def test_guessing_the_mimetype(self):
        self.assertEqual(util.guess_mime_type("/foo/thing.js"), "text/javascript")
        self.assertEqual(util.guess_mime_type("/foo/thing.css"), "text/css")
        self.assertEqual(util.guess_mime_type("/foo/thing.xyz"), "text/html")


class TestCaching(unittest.TestCase):

    def test_cache_control(self):
        headers = dict(util.caching_headers())
        self.assertIn("public", headers["Cache-Control"])
        self.assertIn("immutable", headers["Cache-Control"])

    def test_expires(self):
        headers = dict(util.caching_headers())
        expires = datetime.datetime.strptime(headers["Expires"], "%a, %d %b %Y %H:%M:%S GMT")
        future = datetime.datetime.now() + datetime.timedelta(days=250)
        self.assertGreater(expires, future)
