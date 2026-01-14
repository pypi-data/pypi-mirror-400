import pytest
from pathlib import Path

from yamlpp import Interpreter
from yamlpp.util import print_yaml
from yamlpp.error import YAMLppError
from yamlpp.core import MappingEntry

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------




def write(tmp_path, name, content):
    """Write a file under tmp_path and return its string path."""
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# 1. Short-form import
# ---------------------------------------------------------------------------

def test_import_short_form(tmp_path):
    MODULE_NAME = "mod5"
    content="""
.define:
  foo: 123
"""
    write(tmp_path, f"{MODULE_NAME}.ypp", content)

    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", f"{MODULE_NAME}.ypp")

    i.handle_import(entry)

    assert MODULE_NAME in i.stack
    assert i.stack[MODULE_NAME]["foo"] == 123


# ---------------------------------------------------------------------------
# 2. Long-form import with alias
# ---------------------------------------------------------------------------

def test_import_long_form_alias(tmp_path):
    content="""
.define:
  foo: 123
"""
    write(tmp_path, "mod.ypp", content)
    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", {
        ".filename": "mod.ypp",
        ".as": "m",
    })

    i.handle_import(entry)

    assert "m" in i.stack
    assert i.stack["m"]["foo"] == 123


# ---------------------------------------------------------------------------
# 3. Long-form import with exposes
# ---------------------------------------------------------------------------

SOURCE_FILE = "mod.ypp"

def test_import_exposes(tmp_path):
    VALUES = """
.define:
    foo: 1
    bar: 2
"""
    print("Values:\n", VALUES)
    write(tmp_path, SOURCE_FILE, VALUES)

    i = Interpreter(filename=tmp_path/SOURCE_FILE, source_dir=str(tmp_path), render=True)
    print("Initial tree:", i.initial_tree)
    i.render_tree()

    entry = MappingEntry(".import", {
        ".filename": "mod.ypp",
        ".exposes": ["foo"],
    })

    i.handle_import(entry)

    print("Stack:\n", i.stack)

    assert "foo" in i.stack
    assert i.stack["foo"] == 1
    assert "bar" in i.stack


# ---------------------------------------------------------------------------
# 4. .exposes must be a list
# ---------------------------------------------------------------------------

def test_import_exposes_must_be_list(tmp_path):
    write(tmp_path, SOURCE_FILE, "foo: 1")

    i = Interpreter(filename=tmp_path/SOURCE_FILE, source_dir=str(tmp_path), render=True)
    entry = MappingEntry(".import", {
        ".filename": "mod.ypp",
        ".exposes": "foo",  # invalid
    })

    with pytest.raises(YAMLppError) as exc:
        i.handle_import(entry)

    assert ".exposes expects a list" in str(exc.value)


# ---------------------------------------------------------------------------
# 5. Missing file
# ---------------------------------------------------------------------------

def test_import_missing_file(tmp_path):
    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", "does_not_exist.ypp")

    with pytest.raises(YAMLppError):
        i.handle_import(entry)


# ---------------------------------------------------------------------------
# 6. Missing exposed item
# ---------------------------------------------------------------------------

def test_import_missing_exposed_item(tmp_path):
    content="""
.define:
  foo: 123
"""
    write(tmp_path, "mod.ypp", content)
    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", {
        ".filename": "mod.ypp",
        ".exposes": ["bar"],  # does not exist
    })

    with pytest.raises(YAMLppError) as exc:
        i.handle_import(entry)

    assert "Cannot import item 'bar'" in str(exc.value)


# ---------------------------------------------------------------------------
# 7. Namespace isolation
# ---------------------------------------------------------------------------

def test_import_namespace_isolation(tmp_path):
    """
    When you import a module, its internal names must NOT leak 
    into the caller’s namespace. 
    Instead, the module must appear as a single namespaced object.
    """
    content="""
.define:
  foo: 123
"""
    write(tmp_path, "mod.ypp", content)
    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", "mod.ypp")

    i.handle_import(entry)
    print(i.stack)

    assert "foo" not in i.stack
    assert "mod" in i.stack
    assert i.stack["mod"]["foo"] == 123


# ---------------------------------------------------------------------------
# 8. Golden test: nested imports
# ---------------------------------------------------------------------------

def test_nested_imports(tmp_path):
    """
    A imports B, B exposes foo.
    A should see foo in its stack.
    """
    content="""
.define:
  foo: 42
"""
    write(tmp_path, "b.ypp", content)

    write(tmp_path, "a.ypp", """
.import:
  .filename: b.ypp
  .exposes: [foo]
.print: "foo: {{ foo }}"
""")

    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", "a.ypp")

    i.handle_import(entry)
    print(i.stack)

    # A exposes foo from B
    assert "foo" not in i.stack
    assert i.stack['a']["foo"] == 42


# ---------------------------------------------------------------------------
# 9. Golden test: chained imports with aliasing
# ---------------------------------------------------------------------------

def test_chained_imports_with_alias(tmp_path):
    """
    A imports B as b.
    B imports C and exposes x.
    A should see b.x.
    """
    content="""
.define:
  x: 7
"""
    write(tmp_path, "c.ypp", content)

    write(tmp_path, "b.ypp", """
.import:
  .filename: c.ypp
  .exposes: [x]
""")

    write(tmp_path, "a.ypp", """
.import:
  .filename: b.ypp
  .as: b
""")

    i = Interpreter(source_dir=str(tmp_path))
    entry = MappingEntry(".import", "a.ypp")

    i.handle_import(entry)

    assert "a" in i.stack
    assert i.stack["a"]["b"]["x"] == 7
