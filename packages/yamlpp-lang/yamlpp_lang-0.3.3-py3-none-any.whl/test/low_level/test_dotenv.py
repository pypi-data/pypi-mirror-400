import pytest
from ruamel.yaml.comments import CommentedMap
from yamlpp.dotenv import DotEnv   # adjust to your module name


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------

def test_loads_basic():
    """
    Rationale:
        The simplest invariant: KEY=VALUE pairs must be parsed into strings.

    Expected:
        - Values are always strings (dotenv has no types).
        - Mapping is a CommentedMap.
    """
    text = "A=1\nB=hello"
    cm = DotEnv.loads(text)

    assert isinstance(cm, CommentedMap)
    assert cm["A"] == "1"
    assert cm["B"] == "hello"


# ---------------------------------------------------------------------------
# Parsing with standalone and inline comments
# ---------------------------------------------------------------------------

def test_loads_with_comments():
    """
    Rationale:
        Dotenv must preserve:
        - standalone comments before keys
        - inline comments after values

    Risk:
        Losing comments breaks round-trip fidelity and violates YAMLpp invariants.

    Expected:
        - Pre-comments stored in cm.ca.items[key][1] as a list of strings.
        - Inline comments stored in cm.ca.items[key][2] as a list of strings.
    """
    text = """
# Global config
A=1  # inline
# Another comment
B=hello
"""
    cm = DotEnv.loads(text)

    # Pre-comment for A
    pre_A = cm.ca.items["A"][1]
    assert any("Global config" in c for c in pre_A)

    # Inline comment for A
    inline_A = cm.ca.items["A"][2]
    assert any("inline" in c for c in inline_A)

    # Pre-comment for B
    pre_B = cm.ca.items["B"][1]
    assert any("Another comment" in c for c in pre_B)


# ---------------------------------------------------------------------------
# Blank lines preserved
# ---------------------------------------------------------------------------

def test_loads_blank_lines():
    """
    Rationale:
        Blank lines must be preserved as empty pre-comments.
        This is essential for round-trip fidelity.

    Expected:
        - A blank line becomes "" in the pre-comment list.
    """
    text = """
# First
A=1

# Second
B=2
"""
    cm = DotEnv.loads(text)

    pre_A = cm.ca.items["A"][1]
    assert pre_A == ["# First"]

    pre_B = cm.ca.items["B"][1]
    assert pre_B == ["", "# Second"]


# ---------------------------------------------------------------------------
# Round-trip fidelity
# ---------------------------------------------------------------------------

def test_round_trip():
    """
    Rationale:
        The core invariant: loads(dumps(loads(x))) == loads(x)
        for both values and comments.

    Risk:
        Any deviation breaks YAMLpp backend guarantees.

    Expected:
        - Values preserved
        - Pre-comments preserved
        - Inline comments preserved
    """
    text = """
# SMTP config
SMTP_HOST=smtp.infomaniak.com  # main host

# Credentials
SMTP_USER=contact@example.com
SMTP_PASS=secret
"""
    cm1 = DotEnv.loads(text)
    out = DotEnv.dumps(cm1)
    cm2 = DotEnv.loads(out)

    assert cm2["SMTP_HOST"] == "smtp.infomaniak.com"
    assert cm2["SMTP_USER"] == "contact@example.com"
    assert cm2["SMTP_PASS"] == "secret"

    assert any("SMTP config" in c for c in cm2.ca.items["SMTP_HOST"][1])
    assert any("main host" in c for c in cm2.ca.items["SMTP_HOST"][2])
    assert any("Credentials" in c for c in cm2.ca.items["SMTP_USER"][1])


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_loads_error_missing_equal():
    """
    Rationale:
        Dotenv requires KEY=VALUE. Missing '=' must raise.

    Expected:
        ValueError.
    """
    with pytest.raises(ValueError):
        DotEnv.loads("INVALID_LINE")


def test_loads_error_empty_key():
    """
    Rationale:
        Empty keys are invalid and must not be silently accepted.

    Expected:
        ValueError.
    """
    with pytest.raises(ValueError):
        DotEnv.loads(" =value")


# ---------------------------------------------------------------------------
# dumps(): key validation
# ---------------------------------------------------------------------------

def test_dumps_key_must_be_string():
    """
    Rationale:
        Dotenv keys must be strings. Anything else breaks the format.

    Expected:
        ValueError.
    """
    cm = CommentedMap()
    cm[123] = "value"   # invalid key type

    with pytest.raises(ValueError):
        DotEnv.dumps(cm)


# ---------------------------------------------------------------------------
# dumps(): value validation
# ---------------------------------------------------------------------------

def test_dumps_value_must_be_scalar():
    """
    Rationale:
        Dotenv values must be scalar (str, int, float).
        Nested structures must be rejected.

    Expected:
        ValueError.
    """
    cm = CommentedMap()
    cm["A"] = {"nested": True}  # invalid

    with pytest.raises(ValueError):
        DotEnv.dumps(cm)


# ---------------------------------------------------------------------------
# dumps(): comment preservation
# ---------------------------------------------------------------------------

def test_dumps_preserves_comments():
    """
    Rationale:
        dumps() must preserve:
        - pre-comments
        - inline comments
        - formatting

    Expected:
        - Pre-comment appears before key
        - Inline comment appears after value with a single '#'
    """
    cm = CommentedMap()
    cm["A"] = "1"

    # Populate .ca.items directly with plain strings (no CommentToken)
    cm.ca.items["A"] = [
        None,
        ["# Comment A"],     # pre-comments
        ["# inline A"],      # inline comments
        None
    ]

    out = DotEnv.dumps(cm)

    assert out == "# Comment A\nA=1  # inline A"

