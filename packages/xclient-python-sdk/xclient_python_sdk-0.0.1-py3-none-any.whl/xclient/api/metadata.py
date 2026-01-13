import platform

from importlib import metadata

try:
    version = metadata.version("xclient-python-sdk")
except metadata.PackageNotFoundError:
    version = "dev"

default_headers = {
    "lang": "python",
    "lang_version": platform.python_version(),
    "machine": platform.machine(),
    "os": platform.platform(),
    "package_version": version,
    "processor": platform.processor(),
    "publisher": "xclient",
    "release": platform.release(),
    "sdk_runtime": "python",
    "system": platform.system(),
}

