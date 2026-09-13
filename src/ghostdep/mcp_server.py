from pathlib import Path

import tomllib
from mcp.server.mcpserver import MCPServer

from ghostdep.checker import PackageResult, check_package
from ghostdep.parsers import (
    UnsupportedManifestFormat,
    is_valid_package_name,
    parse_manifest,
)

server = MCPServer(
    name="ghostdep",
    version="0.1.0",
    instructions=(
        "Call check_packages before running `pip install` on any package name "
        "an AI suggested, or check_manifest before installing from a "
        "requirements.txt/pyproject.toml an AI wrote, to catch hallucinated "
        "(non-existent) package names before they reach pip."
    ),
)


def _result_dict(result: PackageResult) -> dict:
    return {"name": result.name, "status": result.status.value, "detail": result.detail}


def _error_dict(name: str, detail: str) -> dict:
    return {"name": name, "status": "error", "detail": detail}


@server.tool()
def check_packages(names: list[str]) -> list[dict]:
    """Check whether each package name actually exists on PyPI.

    Call this before installing any package name an AI suggested (e.g. from
    a suggested `pip install ...` command) to catch a hallucinated
    (non-existent) name before it reaches pip.
    """
    results = []
    for name in names:
        if not is_valid_package_name(name):
            results.append(_error_dict(name, "invalid package name"))
            continue
        results.append(_result_dict(check_package(name)))
    return results


@server.tool()
def check_manifest(file_path: str) -> list[dict]:
    """Check every dependency declared in a requirements.txt or pyproject.toml.

    Call this before installing from a dependency file an AI wrote or edited.
    """
    try:
        names = parse_manifest(Path(file_path))
    except FileNotFoundError:
        return [_error_dict(file_path, "file not found")]
    except UnsupportedManifestFormat as exc:
        return [_error_dict(file_path, str(exc))]
    except tomllib.TOMLDecodeError as exc:
        return [_error_dict(file_path, f"could not parse TOML: {exc}")]

    if not names:
        return [_error_dict(file_path, "no dependencies found")]
    return [_result_dict(check_package(name)) for name in names]


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
