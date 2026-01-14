"""
dotenv.py — Comment-preserving dotenv backend using ruamel.yaml

Invariants:
- Comments in .ca.items are always plain strings, never tokens.
- Pre-comments: list[str], each either "" (blank line) or starting with '#'.
- Inline comments: list[str], each starting with '#'.
- No ruamel comment API is used; we write directly into cm.ca.items.
- Values are always strings on load.
"""

from __future__ import annotations

from collections.abc import Mapping
from ruamel.yaml.comments import CommentedMap

SCALARS = (str, int, float)


class DotEnv:
    """
    Comment-preserving dotenv reader/writer using ruamel CommentedMap,
    under the strict invariant that all comments are stored as plain strings.
    """

    # ------------------------------------------------------------------
    # LOADS
    # ------------------------------------------------------------------

    @staticmethod
    def loads(text: str) -> CommentedMap:
        """
        Parse dotenv text into a CommentedMap with comment preservation.

        - Pre-comments: ["# First", "", "# Another"]
        - Inline comments: ["# inline"]
        - Values: always strings
        """
        cm = CommentedMap()
        pending_pre: list[str] = []
        seen_first_key = False

        for raw_line in text.splitlines():
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            # Blank line
            if not stripped:
                if seen_first_key:
                    pending_pre.append("")
                continue

            # Standalone comment
            if stripped.startswith("#"):
                # Store full syntactic form, including '#'
                pending_pre.append(stripped)
                continue

            # Must contain '='
            if "=" not in stripped:
                raise ValueError(f"Invalid dotenv line (missing '='): {line}")

            key_part, rest = stripped.split("=", 1)
            key = key_part.strip()
            if not key:
                raise ValueError(f"Invalid dotenv line (empty key): {line}")

            # Inline comment
            inline_comment = None
            if "#" in rest:
                value_part, inline_raw = rest.split("#", 1)
                value_str = value_part.rstrip()
                inline_comment = "#" + inline_raw.strip()
            else:
                value_str = rest

            value = value_str.strip()

            # Strip quotes
            if (len(value) >= 2 and
                ((value.startswith('"') and value.endswith('"')) or
                 (value.startswith("'") and value.endswith("'")))):
                value = value[1:-1]

            # Store key/value
            cm[key] = value

            # Build comment arrays (syntactic, strings only)
            pre_list = pending_pre[:] if pending_pre else []
            inline_list = [inline_comment] if inline_comment else []

            # Write directly into ruamel's comment structure, with only strings
            cm.ca.items[key] = [None, pre_list, inline_list, None]

            pending_pre = []
            seen_first_key = True

        return cm

    # ------------------------------------------------------------------
    # DUMPS
    # ------------------------------------------------------------------

    @staticmethod
    def dumps(mapping: Mapping) -> str:
        """
        Serialize a Mapping/CommentedMap into dotenv text.

        - Pre-comments: "# text"
        - Blank lines: ""
        - Inline comments: "  # text"

        Contract:
        - mapping.ca.items[key][1] and [2], if present, MUST be list[str] or None.
        - This backend does not accept CommentToken or other ruamel token objects.
        """
        if not isinstance(mapping, Mapping):
            raise TypeError(f"DotEnv.dumps() expects a mapping, got: {type(mapping)}")

        lines: list[str] = []
        has_ca = hasattr(mapping, "ca") and getattr(mapping, "ca") is not None
        ca_items = mapping.ca.items if has_ca else {}

        for key in mapping:
            # Key validation
            if not isinstance(key, str):
                raise ValueError(f"Dotenv keys must be strings, got: {type(key)}")

            value = mapping[key]

            # Value validation
            if not isinstance(value, SCALARS):
                raise ValueError(f"Dotenv values must be scalar, got: {type(value)}")

            # Pre-comments
            pre_list = []
            if has_ca and key in ca_items:
                pre_node = ca_items[key][1]
                if isinstance(pre_node, list):
                    # Contract: list[str]
                    pre_list = pre_node

            for c in pre_list:
                if c == "":
                    lines.append("")  # blank line
                else:
                    # Contract: already a syntactic comment (starts with '#')
                    lines.append(c)

            # Prepare value string
            val_str = str(value)
            needs_quotes = (
                not val_str
                or val_str[0].isspace()
                or val_str[-1].isspace()
                or any(ch in val_str for ch in (" ", "#", "="))
            )

            if needs_quotes:
                escaped = val_str.replace('"', '\\"')
                val_out = f'"{escaped}"'
            else:
                val_out = val_str

            line = f"{key}={val_out}"

            # Inline comment
            inline_list = []
            if has_ca and key in ca_items:
                inline_node = ca_items[key][2]
                if isinstance(inline_node, list):
                    inline_list = inline_node

            if inline_list:
                raw = inline_list[0].strip()
                # Contract: already starts with '#'
                line += f"  {raw}"

            lines.append(line)

        return "\n".join(lines)
