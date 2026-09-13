import argparse
from pathlib import Path

from ghostdep.checker import Status, check_package
from ghostdep.parsers import is_valid_package_name, parse_manifest


def _collect_names(args: argparse.Namespace) -> list[str]:
    if args.file:
        return parse_manifest(Path(args.file))
    return args.packages


def _format_result(result) -> str:
    if result.status is Status.EXISTS:
        return f"OK        {result.name}"
    if result.status is Status.NOT_FOUND:
        return f"NOT FOUND {result.name}  <-- does not exist on PyPI, do not install"
    return f"ERROR     {result.name}  ({result.detail})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ghostdep",
        description="Verify that package names actually exist on PyPI before you install them.",
    )
    parser.add_argument("packages", nargs="*", help="Package names to check")
    parser.add_argument(
        "--file",
        help="Check every dependency declared in a requirements.txt or pyproject.toml file",
    )
    args = parser.parse_args(argv)

    try:
        names = _collect_names(args)
    except FileNotFoundError:
        parser.error(f"file not found: {args.file}")

    if not names:
        if args.file:
            parser.error(
                f"no dependencies found in {args.file} "
                "(only PEP 621 `[project.dependencies]` is supported; "
                "Poetry-style `[tool.poetry.dependencies]` is not)"
            )
        parser.error("no package names given (pass names directly or use --file)")

    invalid = [name for name in names if not is_valid_package_name(name)]
    if invalid:
        parser.error(f"invalid package name(s): {', '.join(invalid)}")

    exit_code = 0
    for name in names:
        result = check_package(name)
        print(_format_result(result))
        if result.status is not Status.EXISTS:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
