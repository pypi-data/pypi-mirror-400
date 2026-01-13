import subprocess
import sys


def test_cli_check_identical_dirs(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"

    a.mkdir()
    b.mkdir()
    (a / "f.txt").write_text("hello")
    (b / "f.txt").write_text("hello")

    result = subprocess.run(
        [
            sys.executable, "-m", "fsync.cli",
            "check", str(a), str(b)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
