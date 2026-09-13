# ghostdep

An MCP server that lets an AI coding agent check whether a package name
actually exists on PyPI *before* it runs `pip install`.

LLMs regularly hallucinate package names that look real but don't exist —
attackers register those exact names on PyPI with malicious payloads
("slopsquatting"). Existing tools solve this for a human running a CLI or git
hook. `ghostdep` targets the other case: an agent about to install a
dependency autonomously, with no human in the loop to run a separate check
first.

## How it fits into an agent's tool-use loop

```
Claude Code is about to run: pip install requests fastapi fast-super-secure-lib

It calls ghostdep's check_packages(["requests", "fastapi", "fast-super-secure-lib"]) first:

{
  "name": "requests",
  "status": "exists",
  "detail": ""
}
{
  "name": "fastapi",
  "status": "exists",
  "detail": ""
}
{
  "name": "fast-super-secure-lib",
  "status": "not_found",
  "detail": ""
}
```

That's real output from `check_packages`, called over the actual MCP protocol
(stdio, tool discovery, JSON-RPC) against the live PyPI registry — not a
mocked example.

## Setup (MCP server)

```bash
pip install -e .
```

Add to your MCP client's config (e.g. a project's `.mcp.json` for Claude
Code):

```json
{
  "mcpServers": {
    "ghostdep": {
      "command": "/absolute/path/to/.venv/bin/ghostdep-mcp",
      "args": []
    }
  }
}
```

Two tools are exposed:
- `check_packages(names: list[str])` — check an ad-hoc list of names (e.g.
  ones an AI just suggested).
- `check_manifest(file_path: str)` — check every dependency declared in a
  requirements.txt or pyproject.toml.

## CLI (for a human running it directly)

```bash
ghostdep requests some-hallucinated-package
ghostdep --file requirements.txt
ghostdep --file pyproject.toml
```

Exit code is non-zero if any package could not be found on PyPI.

## Development

```bash
pip install -e ".[dev]"
pytest
```
