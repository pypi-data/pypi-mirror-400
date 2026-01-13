\
from pathlib import Path
from rebo.commands.index import parse_makefile_targets

def test_parse_makefile_targets(tmp_path: Path):
    mk = tmp_path / "Makefile"
    mk.write_text("all: a\nclean:\n\t@echo hi\n", encoding="utf-8")
    t = parse_makefile_targets(mk)
    assert "all" in t and "clean" in t
