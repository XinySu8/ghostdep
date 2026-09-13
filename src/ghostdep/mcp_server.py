from pathlib import Path

import tomllib
from mcp.server.mcpserver import MCPServer

from ghostdep.checker import PackageResult, Status, check_package
from ghostdep.parsers import (
    UnsupportedManifestFormat,
    is_valid_package_name,
    parse_manifest,
)
from ghostdep.suggest import suggest_replacement

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
    entry = {"name": result.name, "status": result.status.value, "detail": result.detail}
    if result.status is Status.NOT_FOUND:
        replacement = suggest_replacement(result.name)
        if replacement:
            entry["suggested_replacement"] = replacement
    return entry


def _error_dict(name: str, detail: str) -> dict:
    return {"name": name, "status": "error", "detail": detail}


def _summarize(results: list[dict]) -> dict:
    """Wrap per-package results into a verdict the calling agent can act on
    directly, instead of a report it has to reason over itself.

    suggested_command is built only from names that came back "exists" - a
    suggested_replacement on a NOT_FOUND entry is a plausible guess, not a
    confirmed identity, so it is never auto-substituted into an installable
    command.
    """
    safe_names = [r["name"] for r in results if r["status"] == "exists"]
    blocked = [r["name"] for r in results if r["status"] != "exists"]
    return {
        "results": results,
        "safe_to_install": len(blocked) == 0,
        "blocked": blocked,
        "suggested_command": f"pip install {' '.join(safe_names)}" if safe_names else None,
    }


@server.tool()
def check_packages(names: list[str]) -> dict:
    """Check whether each package name actually exists on PyPI, and return a
    verdict you can act on directly.

    Call this before installing any package name an AI suggested (e.g. from
    a suggested `pip install ...` command) to catch a hallucinated
    (non-existent) name before it reaches pip. If safe_to_install is False,
    do not run the original install command - use suggested_command instead,
    or resolve each blocked name first.
    """
    results = []
    for name in names:
        if not is_valid_package_name(name):
            results.append(_error_dict(name, "invalid package name"))
            continue
        results.append(_result_dict(check_package(name)))
    return _summarize(results)


@server.tool()
def check_manifest(file_path: str) -> dict:
    """Check every dependency declared in a requirements.txt or pyproject.toml,
    and return a verdict you can act on directly.

    Call this before installing from a dependency file an AI wrote or edited.
    """
    try:
        names = parse_manifest(Path(file_path))
    except FileNotFoundError:
        return _summarize([_error_dict(file_path, "file not found")])
    except UnsupportedManifestFormat as exc:
        return _summarize([_error_dict(file_path, str(exc))])
    except tomllib.TOMLDecodeError as exc:
        return _summarize([_error_dict(file_path, f"could not parse TOML: {exc}")])

    if not names:
        return _summarize([_error_dict(file_path, "no dependencies found")])
    return _summarize([_result_dict(check_package(name)) for name in names])


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
