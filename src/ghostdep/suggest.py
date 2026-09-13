import difflib
from pathlib import Path

_POPULAR_PACKAGES_FILE = Path(__file__).parent / "data" / "popular_packages.txt"
_MATCH_CUTOFF = 0.8


def _load_popular_packages() -> list[str]:
    return [
        line
        for line in _POPULAR_PACKAGES_FILE.read_text().splitlines()
        if line and not line.startswith("#")
    ]


_POPULAR_PACKAGES = _load_popular_packages()


def suggest_replacement(name: str) -> str | None:
    """Return the closest popular PyPI package name to `name`, if one is
    close enough to plausibly be what was actually meant; None otherwise.

    Only meaningful for a name already confirmed not to exist on PyPI - this
    is a suggestion for a human/agent to evaluate, not a confirmed identity.
    """
    matches = difflib.get_close_matches(name, _POPULAR_PACKAGES, n=1, cutoff=_MATCH_CUTOFF)
    return matches[0] if matches else None
