import time
from fsync.core import diff_dirs

def test_updated_file_by_mtime(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"

    a.mkdir()
    b.mkdir()

    fa = a / "f.txt"
    fb = b / "f.txt"

    fb.write_text("old")
    time.sleep(1)
    fa.write_text("new")

    diff, _ = diff_dirs(str(a), str(b))

    assert "f.txt" in diff["updated_files"]


