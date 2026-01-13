

from typing import Iterable, Optional, Tuple

import datetime
import os
import tarfile

try:  # introduced in 3.11
    from datetime import UTC  # type: ignore
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


def load_from_package(basedir: str, package: str, version: str,
                      resourcepath: str) -> Optional[bytes]:
    srcpath = f"{basedir}/{package}-{version}.tgz"
    if not os.path.exists(srcpath):
        return None  # scriptkiddie noise
    try:
        return load_from_tarball(srcpath, f"package/{resourcepath}")
    except KeyError:
        return None  # file not in archive


def load_from_tarball(tarball: str, path: str) -> bytes:
    with tarfile.open(tarball, "r:gz") as archive:
        src = archive.extractfile(path)
        assert src is not None
        return src.read()


def guess_mime_type(path: str) -> str:
    if path.endswith(".js"):
        return "text/javascript"
    if path.endswith(".css"):
        return "text/css"  # firefox won't load without this set
    return "text/html"  # is there a better default?!?


def caching_headers() -> Iterable[Tuple[str, str]]:
    yield ("Cache-Control", "public, max-age=31536000, immutable")
    expiry = datetime.datetime.now(tz=UTC) + datetime.timedelta(seconds=31536000)
    yield ("Expires", expiry.strftime("%a, %d %b %Y %H:%M:%S GMT"))
