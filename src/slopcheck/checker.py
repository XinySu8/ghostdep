from dataclasses import dataclass
from enum import Enum

import requests

PYPI_URL = "https://pypi.org/pypi/{name}/json"
TIMEOUT_SECONDS = 5


class Status(Enum):
    EXISTS = "exists"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass
class PackageResult:
    name: str
    status: Status
    detail: str = ""


def check_package(name: str) -> PackageResult:
    """Check whether `name` exists on PyPI.

    Network failures are surfaced as Status.ERROR rather than treated as
    EXISTS or NOT_FOUND, so a flaky connection never gets silently read as
    "safe to install".
    """
    url = PYPI_URL.format(name=name)
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        return PackageResult(name, Status.ERROR, str(exc))

    if response.status_code == 200:
        return PackageResult(name, Status.EXISTS)
    if response.status_code == 404:
        return PackageResult(name, Status.NOT_FOUND)
    return PackageResult(name, Status.ERROR, f"unexpected status {response.status_code}")
