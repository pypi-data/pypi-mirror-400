import json
import subprocess
import sys
from jsonschema import validate


def test_json_schema_validation(tmp_path):
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

    # diff existe → exit code 1 é esperado
    assert result.returncode == 1
    assert out.exists()

    report = json.loads(out.read_text())
    schema = json.loads(open("report.schema.json").read())

    validate(instance=report, schema=schema)
