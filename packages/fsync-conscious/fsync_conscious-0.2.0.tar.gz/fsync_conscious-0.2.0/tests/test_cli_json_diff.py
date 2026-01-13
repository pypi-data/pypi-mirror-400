import subprocess
import sys
import json


def test_cli_json_diff_only(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    out = tmp_path / "diff.json"

    a.mkdir()
    b.mkdir()
    (a / "f.txt").write_text("hello")

    result = subprocess.run(
        [
            sys.executable, "-m", "fsync.cli",
            "diff", str(a), str(b),
            "--json", str(out)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert out.exists()

    diff = json.loads(out.read_text())

    assert "new_files" in diff
    assert "updated_files" in diff
    assert "extra_files" in diff
