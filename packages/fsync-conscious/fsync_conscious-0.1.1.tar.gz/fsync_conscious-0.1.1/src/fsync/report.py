def print_report(diff):
    print("\n📊 DIFF REPORT\n")

    for k, v in diff.items():
        print(f"{k}: {len(v)}")
        for i in v:
            print(f"  - {i}")
        print()


