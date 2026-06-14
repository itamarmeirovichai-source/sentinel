# Contributing to Sentinel

Thanks for looking! Sentinel is an early (alpha) open-source project — issues, ideas, and
PRs are all welcome.

## Dev setup

```bash
make install   # venv + editable install with dev extras
make test      # pytest
make lint      # ruff
```

## Ground rules

- **Tests-first on security-critical code** (policy engine, audit integrity, kill switch).
  Add a test with (or before) the change.
- Keep `ruff check src tests` clean and `pytest` green — CI enforces both (3.11–3.13).
- The audit log is **append-only and tamper-evident** — never add anything that mutates
  past records or breaks the hash chain.
- Be honest in docs: compliance mappings are *indicative engineering aids, not legal advice*.

## Security issues

Report privately — see [SECURITY.md](SECURITY.md). Do not open a public issue for an
unfixed vulnerability.

## License

By contributing, you agree your contributions are licensed under Apache-2.0.
