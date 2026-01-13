from fsync.core import diff_dirs

def test_hash_diff(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"

    a.mkdir()
    b.mkdir()

    (a / "f.txt").write_text("AAA")
    (b / "f.txt").write_text("BBB")

    diff, _ = diff_dirs(str(a), str(b), use_hash=True)

    assert "f.txt" in diff["updated_files"]
