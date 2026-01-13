import sys
import json
import argparse
from datetime import datetime

from fsync.core import diff_dirs, apply_sync
from fsync.report import print_report


def compute_exit_code(report, diff):
    if report["invalid"]:
        return 30
    if report["unreadable"]:
        return 20
    if report["skipped"]:
        return 10
    if any(diff.values()):
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Conscious filesystem diff & sync tool"
    )

    parser.add_argument("mode", choices=["diff", "sync", "check"])
    parser.add_argument("A")
    parser.add_argument("B")

    parser.add_argument("--hash", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--strict-fs", action="store_true")
    parser.add_argument("--audit-only", action="store_true")

    # JSON outputs
    parser.add_argument("--json", help="Export diff-only JSON")
    parser.add_argument("--json-audit", help="Export full audit JSON")

    args = parser.parse_args()

    A, B = (args.B, args.A) if args.reverse else (args.A, args.B)

    diff, report = diff_dirs(A, B, use_hash=args.hash)

    # --- EXECUTION ---
    if args.mode == "sync":
        apply_sync(
            A, B,
            diff,
            report,
            delete=args.delete,
            dry=args.dry_run,
            strict_fs=args.strict_fs
        )

    elif args.mode == "check":
        pass  # handled by exit code

    # --- EXIT CODE ---
    exit_code = compute_exit_code(report, diff)

    # --- HUMAN OUTPUT ---
    if not args.audit_only:
        if args.mode == "diff":
            print_report(diff)

        elif args.mode == "check":
            if exit_code == 0:
                print("✅ DIRECTORIES ARE IDENTICAL")
            else:
                print("❌ DIRECTORIES DIFFER")
                print_report(diff)

    # --- JSON OUTPUTS ---
    if args.json:
        with open(args.json, "w") as f:
            json.dump(diff, f, indent=2)

    if args.json_audit:
        payload = {
            "meta": {
                "fsync_version": "0.2.0",
                "mode": args.mode,
                "source": A,
                "destination": B,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "dry_run": args.dry_run,
                "hash": args.hash,
                "delete": args.delete,
                "strict_fs": args.strict_fs,
            },
            "diff": diff,
            "audit": report,
            "exit_code": exit_code,
        }

        with open(args.json_audit, "w") as f:
            json.dump(payload, f, indent=2)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
