\
import json
from rebo.commands.jsondiff import diff

def test_diff_simple_change():
    out = []
    diff({"a": 1}, {"a": 2}, "$", out, limit=100)
    assert any(c["type"] == "changed" and c["path"] == "$.a" for c in out)

def test_diff_added_removed():
    out = []
    diff({"a": 1}, {"b": 1}, "$", out, limit=100)
    types = {c["type"] for c in out}
    assert "removed" in types and "added" in types
