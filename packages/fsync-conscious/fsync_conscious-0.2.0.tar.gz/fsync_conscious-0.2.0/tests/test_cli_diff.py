import subprocess
import sys


def test_cli_diff_detects_difference(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"

    a.mkdir()
    b.mkdir()
    (a / "f.txt").write_text("hello")

    result = subprocess.run(
        [
            sys.executable, "-m", "fsync.cli",
            "diff", str(a), str(b)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
