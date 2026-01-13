import os
import shutil
import hashlib
from concurrent.futures import ThreadPoolExecutor
import stat

REPORT = {
    "copied": [],
    "skipped": [],
    "unreadable": [],
    "invalid": []
}

def is_valid_filename(name):
    # remove apenas whitespace no fim para teste
    if name.rstrip() != name:
        return False
    return True


def sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, FileNotFoundError):
        return None


def scan_dir(base):
    files = {}
    dirs = set()

    for root, dnames, fnames in os.walk(base, followlinks=False):
        rel = os.path.relpath(root, base)
        dirs.add(rel)

        for f in fnames:
            full = os.path.join(root, f)
            relf = os.path.join(rel, f)

            try:
                st = os.lstat(full)

                # ignora se não for arquivo regular
                if not stat.S_ISREG(st.st_mode):
                    continue

                files[relf] = {
                    "path": full,
                    "mtime": st.st_mtime,
                }

            except FileNotFoundError:
                # arquivo sumiu durante o scan
                continue
            except PermissionError:
                print(f"[WARN] permission denied: {full}")
                continue

    return files, dirs


def compute_hashes(files):
    with ThreadPoolExecutor() as ex:
        results = ex.map(
            lambda p: (p, sha256(files[p]["path"])),
            files
        )

        for path, h in results:
            if h is None:
                files[path]["hash"] = "UNREADABLE"
                REPORT["unreadable"].append(path)
                print(f"[WARN] unreadable file skipped (hash): {path}")
            else:
                files[path]["hash"] = h

            



def diff_dirs(a, b, use_hash=False):
    fa, da = scan_dir(a)
    fb, db = scan_dir(b)

    if use_hash:
        compute_hashes(fa)
        compute_hashes(fb)

    diff = {
        "missing_dirs": sorted(list(da - db)),
        "extra_dirs": sorted(list(db - da)),
        "new_files": [],
        "updated_files": [],
        "extra_files": []
    }

    for f in fa:
        if f not in fb:
            diff["new_files"].append(f)
        else:
            if use_hash:
                ha = fa[f]["hash"]
                hb = fb[f]["hash"]

                if ha != hb:
                    diff["updated_files"].append(f)
            else:
                if fa[f]["mtime"] > fb[f]["mtime"]:
                    diff["updated_files"].append(f)

    for f in fb:
        if f not in fa:
            diff["extra_files"].append(f)

    return diff



def apply_sync(a, b, diff, delete=False, dry=False, strict_fs=""):
    for d in diff["missing_dirs"]:
        target = os.path.join(b, d)
        print(f"[DIR ] {target}")
        if not dry:
            os.makedirs(target, exist_ok=True)

    for f in diff["new_files"] + diff["updated_files"]:
        src = os.path.join(a, f)
        dst = os.path.join(b, f)

        filename = os.path.basename(f)
        if filename.rstrip() != filename:
            REPORT["invalid"].append(f)
            print(f"[INVALID] {f!r}")
            if strict_fs:
                raise RuntimeError("Invalid filename detected")
            continue

        # tentativa lógica de cópia (independente de dry-run)
        if dry:
            REPORT["copied"].append(f)
            print(f"[DRY ] would copy {f}")
            continue

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            REPORT["copied"].append(f)
            print(f"[COPY] {f}")
        except PermissionError:
            REPORT["unreadable"].append(f)
            print(f"[UNREADABLE] {f}")
            if strict_fs:
                raise
        except OSError as e:
            REPORT["invalid"].append(f)
            print(f"[INVALID] {f} ({e})")
            if strict_fs:
                raise

        if not dry:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            try:
                shutil.copy2(src, dst)
            except OSError as e:
                print(f"[WARN] copy failed ({e}): {f}")


    if delete:
        for f in diff["extra_files"]:
            path = os.path.join(b, f)
            print(f"[DEL ] {f}")
            if not dry:
                os.remove(path)

        for d in reversed(diff["extra_dirs"]):
            path = os.path.join(b, d)
            if os.path.isdir(path):
                print(f"[RDIR] {d}")
                if not dry:
                    os.rmdir(path)


