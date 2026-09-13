import argparse
from pathlib import Path

from slopcheck.checker import Status, check_package
from slopcheck.parsers import parse_manifest


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
        prog="slopcheck",
        description="Verify that package names actually exist on PyPI before you install them.",
    )
    parser.add_argument("packages", nargs="*", help="Package names to check")
    parser.add_argument(
        "--file",
        help="Check every dependency declared in a requirements.txt or pyproject.toml file",
    )
    args = parser.parse_args(argv)

    names = _collect_names(args)
    if not names:
        parser.error("no package names given (pass names directly or use --file)")

    exit_code = 0
    for name in names:
        result = check_package(name)
        print(_format_result(result))
        if result.status is not Status.EXISTS:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
