import pytest
from io import StringIO

# Import your loader + global YAML_RT
from yamlpp.util import load_yaml, to_yaml


def test_roundtrip_preserves_comments():
    sample = """\
# top-level comment
root:
  # inside mapping
  key: value  # inline comment
"""

    # Load using your round-trip loader
    text, tree = load_yaml(sample, is_text=True)
    out = to_yaml(tree)
    print(out)

    # Assertions: comments must be preserved
    assert "# top-level comment" in out
    assert "# inside mapping" in out
    assert "value  # inline comment" in out

    # Structural invariants
    assert "root:" in out
    assert "key:" in out
