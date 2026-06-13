# PUBLISHING.md — releasing Sentinel to PyPI

The wheel/sdist build is verified (a clean-venv install works). Publishing is the only
remaining step, and it needs **your** PyPI account — so it is intentionally not automated
to run without you. Two ways:

## ⚠️ Pre-flight: the name

The distribution name in `pyproject.toml` is `sentinel`, which is **likely already taken
on PyPI**. Check <https://pypi.org/project/sentinel/>. If taken, rename the *distribution*
(keep the import name `sentinel`):

```toml
# pyproject.toml
[project]
name = "agent-sentinel"   # or another free name; `import sentinel` stays the same
```

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

`pip install agent-sentinel` (or `sentinel` if the name was free) should work anywhere,
and `sentinel --help` is on PATH. Optional extras: `pip install "agent-sentinel[mcp,otel]"`.
