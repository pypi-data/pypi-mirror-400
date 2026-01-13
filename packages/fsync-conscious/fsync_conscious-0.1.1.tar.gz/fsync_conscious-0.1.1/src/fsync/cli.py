from fsync.core import diff_dirs, apply_sync, REPORT
from fsync.report import print_report
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Advanced directory diff & sync tool")
    parser.add_argument("mode", choices=["diff", "sync", "check"])
    parser.add_argument("A")
    parser.add_argument("B")
    parser.add_argument("--hash", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", help="export report to json")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--strict-fs", action="store_true")
    parser.add_argument("--audit-only", action="store_true")

    args = parser.parse_args()

    A, B = (args.B, args.A) if args.reverse else (args.A, args.B)

    diff = diff_dirs(A, B, use_hash=args.hash)

    if args.mode == "diff":
        print_report(diff)

    elif args.mode == "sync":
        apply_sync(A, B, diff, delete=args.delete, dry=args.dry_run, strict_fs=args.strict_fs)

    elif args.mode == "check":
        if all(len(v) == 0 for v in diff.values()):
            print("✅ DIRECTORIES ARE IDENTICAL")
        else:
            print("❌ DIRECTORIES DIFFER")
            print_report(diff)
            sys.exit(1)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(diff, f, indent=2)

    def exit_with_code():
        if REPORT["invalid"]:
            sys.exit(30)
        if REPORT["unreadable"]:
            sys.exit(20)
        if REPORT["skipped"]:
            sys.exit(10)
        sys.exit(0)
    if args.audit_only:
        print("\nAUDIT REPORT")
        for k, v in REPORT.items():
            print(f"{k}: {len(v)}")
        exit_with_code()



if __name__ == "__main__":
    main()

