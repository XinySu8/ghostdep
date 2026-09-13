# slopcheck

Check whether package names actually exist on PyPI before you install them.

LLMs regularly hallucinate package names that look real but don't exist —
attackers register those exact names on PyPI with malicious payloads
("slopsquatting"). `slopcheck` is a one-command sanity check you run before
`pip install`ing anything an AI suggested.

## Install

```bash
pip install -e .
```

## Usage

Check specific names (e.g. pasted from an AI's suggested `pip install` command):

```bash
slopcheck requests some-hallucinated-package
```

Check every dependency declared in a manifest file:

```bash
slopcheck --file requirements.txt
slopcheck --file pyproject.toml
```

Exit code is non-zero if any package could not be found on PyPI.

## Development

```bash
pip install -e ".[dev]"
pytest
```
