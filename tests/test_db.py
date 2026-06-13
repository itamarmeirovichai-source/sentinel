"""Shared SQLite connection helper — WAL + busy_timeout for concurrency safety."""
from sentinel.db import connect


def test_connect_enables_wal_and_busy_timeout(tmp_path):
    con = connect(str(tmp_path / "x.db"))
    assert con.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    assert con.execute("PRAGMA busy_timeout").fetchone()[0] >= 1000


def test_two_connections_coexist(tmp_path):
    db = str(tmp_path / "x.db")
    a = connect(db)
    a.execute("CREATE TABLE t (x)")
    a.commit()
    b = connect(db)  # reader open while writer commits
    a.execute("INSERT INTO t VALUES (1)")
    a.commit()
    assert b.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
