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

Other tools in this space (there are several — see *Prior art* below) report
findings for a human to read. `ghostdep` returns a **verdict the calling
agent can act on directly**, without a further reasoning step: a
`safe_to_install` flag, which names are `blocked`, and — when it can tell
what was actually meant — a `suggested_replacement` for a likely typo,
carried as data for the agent to weigh rather than silently substituted into
an install command.

Real output, captured over the actual MCP protocol (stdio, tool discovery,
JSON-RPC) against the live PyPI registry — not a mocked example — from:

```
Claude Code is about to run: pip install requests reqeusts fastapi

It calls check_packages(["requests", "reqeusts", "fastapi"]) first:
```
```json
{
  "results": [
    { "name": "requests", "status": "exists", "detail": "" },
    { "name": "reqeusts", "status": "not_found", "detail": "",
      "suggested_replacement": "requests" },
    { "name": "fastapi", "status": "exists", "detail": "" }
  ],
  "safe_to_install": false,
  "blocked": ["reqeusts"],
  "suggested_command": "pip install requests fastapi"
}
```

`reqeusts` isn't just flagged — the agent gets `"suggested_replacement":
"requests"` back to evaluate, and `suggested_command` only ever contains
names that came back `exists`, never a guessed replacement: a typo match is
a suggestion, not a confirmed identity.

## Prior art

Several tools already exist in this space — [0xToxSec/slopcheck](https://github.com/0xToxSec/slopcheck)
(CLI/git-hook, 7 ecosystems), [DepScope MCP](https://github.com/cuttalo/depscope-mcp),
[depsentinel-guard](https://pypi.org/project/depsentinel-guard/), and others.
`ghostdep` doesn't try to out-feature them; it's narrower on purpose (PyPI
only) and spends that focus on shaping output an agent can act on without a
human reading it first.

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

Two tools are exposed, both returning the verdict shape shown above:
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

A `NOT FOUND` line also suggests a likely-intended replacement when one is
close enough:

```
$ ghostdep reqeusts
NOT FOUND reqeusts  <-- does not exist on PyPI, do not install -- did you mean 'requests'?
```

Exit code is non-zero if any package could not be found on PyPI.

## Development

```bash
pip install -e ".[dev]"
pytest
```
