"""Kill-switch contract — written before the implementation.

Must be persisted (survive a restart) and support global + per-agent scope.
"""
from sentinel.killswitch import KillSwitch


def test_arm_and_disarm_global(tmp_path):
    ks = KillSwitch(str(tmp_path / "a.db"))
    assert ks.is_active("agentX") is False
    ks.arm("*", reason="incident")
    assert ks.is_active("agentX") is True
    ks.disarm("*")
    assert ks.is_active("agentX") is False


def test_per_agent_scope(tmp_path):
    ks = KillSwitch(str(tmp_path / "a.db"))
    ks.arm("agentA", reason="bad behavior")
    assert ks.is_active("agentA") is True
    assert ks.is_active("agentB") is False


def test_persists_across_instances(tmp_path):
    db = str(tmp_path / "a.db")
    KillSwitch(db).arm("*", reason="x")
    # simulate a process restart: brand-new instance, same DB
    assert KillSwitch(db).is_active("anything") is True
