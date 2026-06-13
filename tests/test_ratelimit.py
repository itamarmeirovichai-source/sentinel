"""Persistent rate-limiter contract — written before the implementation.

Unlike the in-memory limiter, this one shares state across processes/restarts via
SQLite, so the throttle actually holds for a long-running agent.
"""
from sentinel.ratelimit import SqliteRateLimiter


def test_sliding_window_blocks_over_threshold(tmp_path):
    t = {"now": 1000.0}
    rl = SqliteRateLimiter(str(tmp_path / "rl.db"), clock=lambda: t["now"])
    for _ in range(3):
        assert rl.allow("k", 3, 60) is True
    assert rl.allow("k", 3, 60) is False
    t["now"] += 61  # window passes
    assert rl.allow("k", 3, 60) is True


def test_state_persists_across_instances(tmp_path):
    db = str(tmp_path / "rl.db")
    t = {"now": 1000.0}
    rl = SqliteRateLimiter(db, clock=lambda: t["now"])
    for _ in range(3):
        rl.allow("k", 3, 60)
    # brand-new instance, same DB -> still throttled
    assert SqliteRateLimiter(db, clock=lambda: t["now"]).allow("k", 3, 60) is False


def test_keys_are_independent(tmp_path):
    rl = SqliteRateLimiter(str(tmp_path / "rl.db"))
    assert rl.allow("a", 1, 60) is True
    assert rl.allow("a", 1, 60) is False
    assert rl.allow("b", 1, 60) is True
