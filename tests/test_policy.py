"""Policy engine contract — written before the implementation (security-critical)."""
from sentinel.models import Decision, ToolCall
from sentinel.policy import Policy


def mk(tool, **args):
    return ToolCall(tool=tool, args=args, agent_id="a1", session_id="s1")


def test_default_deny_when_no_rule_matches():
    p = Policy.from_yaml("version: 1\ndefault: deny\nrules: []\n")
    r = p.evaluate(mk("anything"))
    assert r.decision == Decision.BLOCK
    assert r.rule_id is None
    assert "default" in r.reason.lower()


def test_glob_tool_allow_and_default_deny_fallthrough():
    p = Policy.from_yaml(
        """
version: 1
default: deny
rules:
  - id: reads
    match: { tool: ["get_*", "read_*"] }
    action: allow
"""
    )
    assert p.evaluate(mk("get_quote")).decision == Decision.ALLOW
    assert p.evaluate(mk("read_file")).decision == Decision.ALLOW
    assert p.evaluate(mk("place_order")).decision == Decision.BLOCK  # nothing matched


def test_arg_comparator_then_fallthrough_rule():
    p = Policy.from_yaml(
        """
version: 1
default: deny
rules:
  - id: cap
    match:
      tool: place_order
      args: { amount: { gt: 500 } }
    action: require_approval
  - id: small_orders
    match: { tool: place_order }
    action: allow
"""
    )
    assert p.evaluate(mk("place_order", amount=1000)).decision == Decision.REQUIRE_APPROVAL
    assert p.evaluate(mk("place_order", amount=100)).decision == Decision.ALLOW


def test_first_match_wins():
    p = Policy.from_yaml(
        """
version: 1
default: deny
rules:
  - id: forbid_deletes
    match: { tool: "delete_*" }
    action: block
  - id: allow_all
    match: { tool: "*" }
    action: allow
"""
    )
    assert p.evaluate(mk("delete_db")).decision == Decision.BLOCK
    assert p.evaluate(mk("get_x")).decision == Decision.ALLOW


def test_rate_limit_blocks_over_threshold_and_recovers():
    t = {"now": 1000.0}
    p = Policy.from_yaml(
        """
version: 1
default: deny
rules:
  - id: rl
    match: { tool: place_order }
    rate_limit: { max: 3, per_seconds: 60 }
    action: allow
""",
        clock=lambda: t["now"],
    )
    for _ in range(3):
        assert p.evaluate(mk("place_order", amount=1)).decision == Decision.ALLOW
    over = p.evaluate(mk("place_order", amount=1))
    assert over.decision == Decision.BLOCK
    assert "rate" in over.reason.lower()
    t["now"] += 61  # window passes
    assert p.evaluate(mk("place_order", amount=1)).decision == Decision.ALLOW


def test_in_comparator_and_default_allow():
    p = Policy.from_yaml(
        """
version: 1
default: allow
rules:
  - id: block_meme_stocks
    match:
      tool: place_order
      args: { symbol: { in: ["TSLA", "GME"] } }
    action: block
"""
    )
    assert p.evaluate(mk("place_order", symbol="TSLA")).decision == Decision.BLOCK
    assert p.evaluate(mk("place_order", symbol="AAPL")).decision == Decision.ALLOW
