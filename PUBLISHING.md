# PUBLISHING.md — releasing Sentinel to PyPI

The wheel/sdist build is verified (a clean-venv install works). Publishing is the only
remaining step, and it needs **your** PyPI account — so it is intentionally not automated
to run without you. Two ways:

## The name (resolved)

The PyPI distribution name is **`agentledger`**. `sentinel`, `agent-sentinel`,
`sentinel-agent`, and `agentwarden` are all already taken (several by AI-agent-security
projects). The **brand stays "Sentinel"** and the import name + CLI are still `sentinel`:

```
pip install agentledger   →   import sentinel   ·   sentinel --help
```

Verified free 2026-06-13. (If you ever want brand == package, it's a mechanical rename of `src/sentinel`.)

## Option A — Trusted Publishing (recommended, no tokens)

One-time setup on PyPI:
1. Create the project (or reserve the name) on PyPI.
2. PyPI → your project → **Publishing** → add a **Trusted Publisher**:
   - Owner: your GitHub user/org · Repository: `sentinel`
   - Workflow: `release.yml` · Environment: `pypi`
3. In GitHub → repo → Settings → Environments, create an environment named `pypi`.

Then every release is just a tag:
```bash
# bump version in pyproject.toml + CHANGELOG.md first, then:
git tag v0.1.0
git push origin v0.1.0     # triggers .github/workflows/release.yml -> builds + publishes
```

## Option B — manual (API token)

```bash
pip install build twine
python -m build
twine upload dist/*        # username: __token__   password: <your pypi token>
```

## After publishing

`pip install agentledger` should work anywhere, and `sentinel --help` is on PATH.
Optional extras: `pip install "agentledger[mcp,otel]"`.
