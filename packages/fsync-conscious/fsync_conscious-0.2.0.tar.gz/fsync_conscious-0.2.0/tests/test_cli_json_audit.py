import subprocess
import sys
import json


def test_cli_json_audit_dry_run(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    out = tmp_path / "report.json"

    a.mkdir()
    b.mkdir()
    (a / "f.txt").write_text("hello")

    result = subprocess.run(
        [
            sys.executable, "-m", "fsync.cli",
            "sync", str(a), str(b),
            "--dry-run",
            "--json-audit", str(out),
            "--audit-only"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert out.exists()

    data = json.loads(out.read_text())

    assert data["meta"]["dry_run"] is True
    assert "f.txt" in data["diff"]["new_files"]
    assert "f.txt" in data["audit"]["copied"]
