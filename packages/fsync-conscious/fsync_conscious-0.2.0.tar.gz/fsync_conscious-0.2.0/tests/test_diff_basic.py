import os
from fsync.core import diff_dirs

def test_new_file(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"

    a.mkdir()
    b.mkdir()

    (a / "file.txt").write_text("hello")

    diff, report = diff_dirs(str(a), str(b))

    assert "file.txt" in diff["new_files"]
    assert diff["updated_files"] == []
    assert diff["extra_files"] == []
