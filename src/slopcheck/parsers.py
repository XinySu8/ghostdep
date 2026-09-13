import re
import tomllib
from pathlib import Path

# A PyPI-style package name: starts alphanumeric, then letters/digits/._-
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")

_SKIP_PREFIXES = ("-e ", "-r ", "--", "http://", "https://", "git+")


def _extract_name(spec: str) -> str | None:
    spec = spec.strip()
    if not spec or spec.startswith("#") or spec.startswith(_SKIP_PREFIXES):
        return None
    spec = spec.split("[", 1)[0]  # drop extras: package[extra]
    spec = spec.split(";", 1)[0]  # drop environment markers
    match = _NAME_RE.match(spec.strip())
    return match.group(0) if match else None


def parse_requirements_txt(path: Path) -> list[str]:
    names = []
    for line in path.read_text().splitlines():
        name = _extract_name(line)
        if name:
            names.append(name)
    return names


def parse_pyproject_toml(path: Path) -> list[str]:
    data = tomllib.loads(path.read_text())
    raw_deps = data.get("project", {}).get("dependencies", [])
    names = []
    for dep in raw_deps:
        name = _extract_name(dep)
        if name:
            names.append(name)
    return names


def parse_manifest(path: Path) -> list[str]:
    if path.name == "pyproject.toml":
        return parse_pyproject_toml(path)
    return parse_requirements_txt(path)


def is_valid_package_name(name: str) -> bool:
    """True if `name` is safe to interpolate into the PyPI lookup URL.

    Names parsed from a manifest already go through _NAME_RE and are always
    valid; this guards names typed directly on the command line, which
    otherwise reach checker.check_package unvalidated.
    """
    return bool(_NAME_RE.fullmatch(name))
